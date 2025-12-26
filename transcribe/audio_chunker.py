#!/usr/bin/env python3
"""
Audio Chunker for OpenAI Whisper API

Splits large audio files into chunks under 25MB using silence detection
for conversation-aware splitting, then transcribes using OpenAI's Whisper API.
"""

import argparse
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

from openai import OpenAI
from pydub import AudioSegment
from pydub.silence import split_on_silence

MAX_CHUNK_BYTES = 25 * 1024 * 1024  # 25MB
MAX_DIARIZE_DURATION_MS = 1300 * 1000  # 1300 seconds (API limit is 1400s for diarization)


def load_audio(path: Path) -> AudioSegment:
    """Load an audio file."""
    return AudioSegment.from_file(str(path))


def get_format_from_path(path: Path) -> str:
    """Get the audio format from file extension."""
    ext = path.suffix.lower().lstrip(".")
    # Map common extensions to pydub format names
    format_map = {
        "mp3": "mp3",
        "mp4": "mp4",
        "m4a": "mp4",
        "wav": "wav",
        "webm": "webm",
        "ogg": "ogg",
        "flac": "flac",
        "mpeg": "mp3",
        "mpga": "mp3",
    }
    return format_map.get(ext, ext)


def get_segment_size(segment: AudioSegment, format: str) -> int:
    """Get the size of an audio segment when exported to the given format."""
    buffer = io.BytesIO()
    segment.export(buffer, format=format)
    return buffer.tell()


def calibrate_bytes_per_ms(audio: AudioSegment, format: str) -> float:
    """Calibrate bytes-per-millisecond by exporting a small sample."""
    sample_duration = min(10000, len(audio))  # 10 seconds max
    sample = audio[:sample_duration]
    size = get_segment_size(sample, format)
    return size / sample_duration


def estimate_size(duration_ms: int, bytes_per_ms: float) -> int:
    """Estimate size based on duration with 10% safety margin."""
    return int(duration_ms * bytes_per_ms * 1.1)


def split_at_silence(audio: AudioSegment) -> list[AudioSegment]:
    """
    Split audio at silence points for conversation-aware chunking.

    Uses parameters optimized for speech:
    - min_silence_len: 500ms (typical sentence pause)
    - silence_thresh: -40 dBFS (speech threshold)
    - keep_silence: 250ms (padding to avoid abrupt cuts)
    """
    segments = split_on_silence(
        audio,
        min_silence_len=500,
        silence_thresh=-40,
        keep_silence=250,
    )

    # If no silence detected, return the whole audio as one segment
    if not segments:
        return [audio]

    return segments


def combine_segments_to_chunks(
    segments: list[AudioSegment],
    format: str,
    bytes_per_ms: float,
    max_bytes: int = MAX_CHUNK_BYTES,
    max_duration_ms: int | None = None,
) -> list[AudioSegment]:
    """
    Combine small segments into chunks that don't exceed max_bytes or max_duration_ms.

    Uses bytes_per_ms ratio to estimate sizes instantly instead of exporting.
    """
    if not segments:
        return []

    chunks = []
    current_chunk = AudioSegment.empty()
    current_duration_ms = 0

    def exceeds_limits(duration_ms: int) -> bool:
        """Check if duration exceeds size or duration limits."""
        if estimate_size(duration_ms, bytes_per_ms) > max_bytes:
            return True
        if max_duration_ms and duration_ms > max_duration_ms:
            return True
        return False

    for segment in segments:
        segment_duration = len(segment)
        test_duration = current_duration_ms + segment_duration

        if exceeds_limits(test_duration):
            # Current chunk is full, save it and start new one
            if len(current_chunk) > 0:
                chunks.append(current_chunk)

            # Check if single segment exceeds limit
            if exceeds_limits(segment_duration):
                # Split large segment by duration
                sub_chunks = split_large_segment(segment, format, max_bytes, bytes_per_ms, max_duration_ms)
                chunks.extend(sub_chunks[:-1])
                current_chunk = sub_chunks[-1] if sub_chunks else AudioSegment.empty()
                current_duration_ms = len(current_chunk)
            else:
                current_chunk = segment
                current_duration_ms = segment_duration
        else:
            current_chunk = current_chunk + segment
            current_duration_ms = test_duration

    # Don't forget the last chunk
    if len(current_chunk) > 0:
        chunks.append(current_chunk)

    return chunks


def split_large_segment(
    segment: AudioSegment,
    format: str,
    max_bytes: int,
    bytes_per_ms: float,
    max_duration_ms: int | None = None,
) -> list[AudioSegment]:
    """Split a segment that's too large by duration or size."""
    duration_ms = len(segment)

    # Calculate chunk duration based on size limit
    size_based_duration = int(max_bytes / (bytes_per_ms * 1.1))

    # Use the smaller of size-based or duration-based limit
    if max_duration_ms:
        chunk_duration_ms = min(size_based_duration, max_duration_ms)
    else:
        chunk_duration_ms = size_based_duration

    chunks = []
    start = 0
    while start < duration_ms:
        end = min(start + chunk_duration_ms, duration_ms)
        chunks.append(segment[start:end])
        start = end

    return chunks


def export_chunks(
    chunks: list[AudioSegment],
    output_dir: Path,
    format: str,
    input_name: str,
) -> list[Path]:
    """Export chunks to files and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    for i, chunk in enumerate(chunks):
        filename = f"{input_name}_chunk_{i:03d}.{format}"
        path = output_dir / filename
        chunk.export(str(path), format=format)
        paths.append(path)
        file_size_mb = path.stat().st_size / 1024 / 1024
        print(f"Exported: {path} ({file_size_mb:.2f} MB)", flush=True)

    return paths


def transcribe_chunk(
    client: OpenAI,
    chunk_path: Path,
    model: str,
    diarize: bool,
    translate: bool = False,
) -> dict:
    """Transcribe or translate a single chunk using OpenAI API."""
    with open(chunk_path, "rb") as audio_file:
        if translate:
            # Translation endpoint only supports whisper-1
            response = client.audio.translations.create(
                model="whisper-1",
                file=audio_file,
            )
        elif diarize:
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe-diarize",
                file=audio_file,
                response_format="diarized_json",
                chunking_strategy="auto",
            )
        else:
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
            )
    return response


def format_diarized_transcript(segments: list) -> str:
    """Format diarized segments into readable text."""
    lines = []
    current_speaker = None
    current_text = []

    for segment in segments:
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "").strip()

        if speaker != current_speaker:
            if current_text:
                lines.append(f"[{current_speaker}]: {' '.join(current_text)}")
            current_speaker = speaker
            current_text = [text] if text else []
        else:
            if text:
                current_text.append(text)

    # Don't forget the last speaker's text
    if current_text:
        lines.append(f"[{current_speaker}]: {' '.join(current_text)}")

    return "\n\n".join(lines)


def split_text_into_chunks(text: str, max_chars: int = 8000) -> list[str]:
    """Split text into smaller chunks for processing."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def translate_text(text: str, client: OpenAI) -> str:
    """Translate text to English using GPT-4o."""
    print("Translating transcript to English...", flush=True)

    # Split into smaller pieces to avoid output truncation
    text_chunks = split_text_into_chunks(text, max_chars=8000)
    translated_parts = []

    for i, chunk in enumerate(text_chunks):
        if len(text_chunks) > 1:
            print(f"  Translating part {i+1}/{len(text_chunks)}...", flush=True)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional medical translator. Translate the following Turkish therapy session transcript to English.

CONTEXT: This is the patient's own recording of their therapy session, being translated for their personal medical records. The patient has full consent and ownership of this content.

INSTRUCTIONS:
1. Translate ALL content faithfully and completely - do not skip, summarize, or censor anything
2. Preserve all formatting including speaker labels like **Me:** and **Therapist:**
3. Keep the same structure and paragraph breaks
4. This is legitimate medical documentation - translate everything as-is
5. Output only the complete translation, nothing else""",
                    },
                    {"role": "user", "content": chunk},
                ],
            )
            result = response.choices[0].message.content

            # Check for actual refusals (starts with refusal phrase)
            refusal_phrases = ["I can't assist", "I cannot assist", "I'm not able", "I am not able", "I'm sorry, but I can't", "I cannot help"]
            is_refusal = any(result.strip().startswith(phrase) for phrase in refusal_phrases) if result else True

            if result and not is_refusal:
                translated_parts.append(result)
            else:
                print(f"  Warning: GPT refused translation, keeping original", flush=True)
                translated_parts.append(chunk)

        except Exception as e:
            print(f"  Error translating part: {e}", flush=True)
            translated_parts.append(chunk)

    return "\n\n".join(translated_parts)


def format_conversation(text: str, client: OpenAI) -> str:
    """Fix grammar and format as a 2-person conversation using GPT-4o."""
    print("Formatting as conversation and fixing grammar...", flush=True)

    # Split into smaller pieces to avoid output truncation
    text_chunks = split_text_into_chunks(text, max_chars=8000)
    formatted_parts = []

    for i, chunk in enumerate(text_chunks):
        if len(text_chunks) > 1:
            print(f"  Processing part {i+1}/{len(text_chunks)}...", flush=True)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional medical transcriptionist formatting a therapy session transcript.

CONTEXT: This is the patient's own recording of their therapy session, being formatted for their personal medical records. The patient has full consent and ownership of this content.

SPEAKER IDENTIFICATION RULES:
- **Me:** = the PATIENT sharing personal experiences, struggles, relationships, feelings, life events
- **Therapist:** = the PROFESSIONAL who listens, asks questions, reflects, provides guidance

The therapist would NEVER share personal stories, relationships, or say things like "I broke up with someone."
The therapist WOULD ask questions, validate feelings, provide observations, schedule appointments.

YOUR TASK:
1. PRESERVE ALL CONTENT completely - do not summarize, skip, or censor anything
2. Identify speakers based on CONTENT (who shares personal stories vs who asks questions)
3. Fix grammar, spelling, and transcription errors
4. Combine fragmented sentences
5. Format as:
   **Me:** [patient's words]
   **Therapist:** [therapist's words]
6. This is legitimate medical documentation - process everything faithfully
7. Output ONLY the complete formatted conversation""",
                    },
                    {"role": "user", "content": chunk},
                ],
            )
            result = response.choices[0].message.content

            # Check for actual refusals (starts with refusal phrase)
            refusal_phrases = ["I can't assist", "I cannot assist", "I'm not able", "I am not able", "I'm sorry, but I can't", "I cannot help"]
            is_refusal = any(result.strip().startswith(phrase) for phrase in refusal_phrases) if result else True

            if result and not is_refusal:
                formatted_parts.append(result)
            else:
                # Fallback: return raw text with basic formatting
                print("  Warning: GPT refused, using raw text", flush=True)
                formatted_parts.append(f"**[Raw transcript]:**\n{chunk}")

        except Exception as e:
            print(f"  Error processing part: {e}", flush=True)
            formatted_parts.append(f"**[Raw transcript]:**\n{chunk}")

    return "\n\n".join(formatted_parts)


def transcribe_chunks(
    chunk_paths: list[Path],
    model: str,
    diarize: bool,
    translate: bool = False,
) -> str:
    """Transcribe or translate all chunks and combine the results."""
    client = OpenAI()  # Uses OPENAI_API_KEY env var

    all_text = []
    all_segments = []

    action = "Translating" if translate else "Transcribing"
    for i, path in enumerate(chunk_paths):
        print(f"{action} chunk {i + 1}/{len(chunk_paths)}: {path.name}", flush=True)
        response = transcribe_chunk(client, path, model, diarize, translate)

        if diarize:
            # diarized_json response has segments with speaker info
            if hasattr(response, "segments"):
                all_segments.extend(response.segments)
            elif isinstance(response, dict) and "segments" in response:
                all_segments.extend(response["segments"])
            else:
                # Fallback to text
                all_text.append(response.text if hasattr(response, "text") else str(response))
        else:
            all_text.append(response.text if hasattr(response, "text") else str(response))

    if diarize and all_segments:
        return format_diarized_transcript(all_segments)

    return "\n".join(all_text)


def chunk_audio(
    input_path: Path,
    output_dir: Path,
    diarize: bool = False,
) -> list[Path]:
    """Main function to chunk an audio file."""
    print(f"Loading audio: {input_path}", flush=True)
    audio = load_audio(input_path)
    format = get_format_from_path(input_path)

    duration_sec = len(audio) / 1000
    print(f"Audio duration: {duration_sec:.1f} seconds", flush=True)

    # Calibrate size estimation
    print(f"Calibrating size estimation...", flush=True)
    bytes_per_ms = calibrate_bytes_per_ms(audio, format)

    print(f"Splitting at silence points (this may take a while for long files)...", flush=True)
    segments = split_at_silence(audio)
    print(f"Found {len(segments)} segments", flush=True)

    # Set duration limit for diarization (API limit is 1400s)
    max_duration_ms = MAX_DIARIZE_DURATION_MS if diarize else None
    limit_msg = "max 25MB" if not diarize else "max 25MB / 21 min"
    print(f"Combining segments into chunks ({limit_msg})...", flush=True)
    chunks = combine_segments_to_chunks(segments, format, bytes_per_ms, max_duration_ms=max_duration_ms)
    print(f"Created {len(chunks)} chunks", flush=True)

    input_name = input_path.stem
    chunk_paths = export_chunks(chunks, output_dir, format, input_name)

    return chunk_paths


def get_chunk_files(directory: Path) -> list[Path]:
    """Get all audio chunk files from a directory, sorted by name."""
    audio_extensions = {".mp3", ".mp4", ".m4a", ".wav", ".webm", ".ogg", ".flac"}
    chunks = [f for f in directory.iterdir() if f.suffix.lower() in audio_extensions]
    return sorted(chunks)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Split audio files into 25MB chunks and transcribe with OpenAI Whisper API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe audio file (chunks saved to /tmp, auto-cleaned)
  audio-chunker recording.m4a --output transcript.txt

  # Transcribe existing chunks folder
  audio-chunker ./chunks/ --output transcript.txt

  # Full therapy session workflow (transcribe, format, translate)
  audio-chunker recording.m4a --format-conversation --output transcript.txt
        """,
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Path to audio file OR directory containing chunk files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save transcript to file (default: print to stdout)",
    )
    parser.add_argument(
        "--no-transcribe",
        action="store_true",
        help="Only chunk, don't transcribe",
    )
    parser.add_argument(
        "--keep-chunks",
        action="store_true",
        help="Don't delete temporary chunk files after processing",
    )
    parser.add_argument(
        "--diarize",
        action="store_true",
        help="Enable speaker diarization (uses gpt-4o-transcribe-diarize)",
    )
    parser.add_argument(
        "--format-conversation",
        action="store_true",
        help="Format as 2-person therapy conversation (Me/Therapist) and fix grammar",
    )
    parser.add_argument(
        "--model",
        default="whisper-1",
        choices=["whisper-1", "gpt-4o-transcribe"],
        help="Model to use for transcription (default: whisper-1)",
    )

    args = parser.parse_args()

    # Validate input exists
    if not args.input.exists():
        print(f"Error: Input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Check for API key if transcribing
    if not args.no_transcribe and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    temp_dir = None
    chunk_paths = []

    try:
        if args.input.is_dir():
            # Input is a directory of existing chunks
            print(f"Using existing chunks from: {args.input}", flush=True)
            chunk_paths = get_chunk_files(args.input)
            if not chunk_paths:
                print(f"Error: No audio files found in {args.input}", file=sys.stderr)
                sys.exit(1)
            print(f"Found {len(chunk_paths)} chunk files", flush=True)
        else:
            # Input is an audio file - chunk it to /tmp
            temp_dir = Path(tempfile.mkdtemp(prefix="audio-chunker-"))
            print(f"Chunking audio to temp directory: {temp_dir}", flush=True)
            chunk_paths = chunk_audio(args.input, temp_dir, diarize=args.diarize)

            if args.no_transcribe:
                print(f"\nChunking complete. {len(chunk_paths)} chunks saved to {temp_dir}")
                if not args.keep_chunks:
                    print("Use --keep-chunks to preserve the chunk files")
                return

        # Process each chunk
        client = OpenAI()
        all_transcripts = []

        for i, chunk_path in enumerate(chunk_paths):
            print(f"\n--- Processing chunk {i + 1}/{len(chunk_paths)}: {chunk_path.name} ---", flush=True)

            # Step 1: Transcribe
            print(f"Transcribing with {args.model}...", flush=True)
            with open(chunk_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model=args.model,
                    file=audio_file,
                )
            raw_text = response.text

            if args.format_conversation:
                # Step 2: Format as conversation
                chunk_transcript = format_conversation(raw_text, client)
                # Step 3: Translate to English
                chunk_transcript = translate_text(chunk_transcript, client)
            else:
                chunk_transcript = raw_text

            all_transcripts.append(chunk_transcript)

        # Combine all chunks
        transcript = "\n\n---\n\n".join(all_transcripts)

        # Output transcript
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(transcript)
            print(f"\nTranscript saved to: {args.output}")
        else:
            print("\n" + "=" * 50)
            print("TRANSCRIPT")
            print("=" * 50)
            print(transcript)

    finally:
        # Cleanup temp chunks
        if temp_dir and temp_dir.exists() and not args.keep_chunks:
            print(f"\nCleaning up temp chunks: {temp_dir}", flush=True)
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()

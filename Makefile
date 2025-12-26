.PHONY: build transcribe help

# Build the transcribe Docker image
build:
	docker build -t mindwork-transcribe ./transcribe

# Transcribe an audio file (full processing: transcribe + format + translate)
# Usage: make transcribe FILE=session.m4a OUTPUT=transcript.txt
transcribe:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make transcribe FILE=<audio-file> OUTPUT=<output-file>"; \
		exit 1; \
	fi
	docker run --rm \
		-e OPENAI_API_KEY \
		-v $(PWD):/data \
		mindwork-transcribe /data/$(FILE) --format-conversation $(if $(OUTPUT),--output /data/$(OUTPUT))

# Raw transcription without formatting
transcribe-raw:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make transcribe-raw FILE=<audio-file> OUTPUT=<output-file>"; \
		exit 1; \
	fi
	docker run --rm \
		-e OPENAI_API_KEY \
		-v $(PWD):/data \
		mindwork-transcribe /data/$(FILE) $(if $(OUTPUT),--output /data/$(OUTPUT))

help:
	@echo "Mindwork - Therapy Session Analysis Toolkit"
	@echo ""
	@echo "Usage:"
	@echo "  make build                              Build Docker image"
	@echo "  make transcribe FILE=s.m4a OUTPUT=t.txt Full processing (format + translate)"
	@echo "  make transcribe-raw FILE=s.m4a          Raw transcription only"

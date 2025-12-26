# Mindwork

A Claude Code plugin for therapy session analysis and personal journaling. Transcribe recordings, extract patterns, track progress, and gain insights from your mental wellness journey.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MINDWORK                                       │
│         Your AI-powered companion for therapy and self-reflection          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Audio Recording ───► transcribe ───► Transcript                          │
│                                              │                              │
│   Journal Entry ─────────────────────────────┤                              │
│                                              ▼                              │
│                                         ┌─────────┐                         │
│                                         │ analyze │                         │
│                                         └────┬────┘                         │
│                                              │                              │
│                    ┌─────────────────────────┼─────────────────────────┐    │
│                    │                         │                         │    │
│                    ▼                         ▼                         ▼    │
│              ┌──────────┐             ┌──────────┐             ┌─────────┐  │
│              │ progress │             │ insights │             │ summary │  │
│              │  (how    │             │  (who    │             │ (what   │  │
│              │  things  │             │  you     │             │ happened│  │
│              │  change) │             │  are)    │             │ quickly)│  │
│              └──────────┘             └──────────┘             └─────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## How It Works

Mindwork is a suite of 5 interconnected skills that help you understand your therapy journey:

### The Pipeline

1. **Input**: You provide therapy session recordings or journal entries
2. **Transcribe**: Audio files are converted to clean, formatted text
3. **Analyze**: Each session/entry is analyzed for patterns, themes, and insights
4. **Build Knowledge**: Over time, the system tracks your progress, builds your profile, and provides summaries

### What Each Skill Does

| Skill | Question It Answers | Input | Output |
|-------|---------------------|-------|--------|
| `transcribe` | "What was said?" | Audio file | Formatted transcript |
| `analyze` | "What patterns are in this session?" | Transcript/journal | Detailed analysis |
| `progress` | "How am I changing over time?" | Multiple analyses | Trend reports |
| `insights` | "Who am I? What are my patterns?" | All analyses | Living profile |
| `summary` | "What happened, quickly?" | Any content | Condensed summary |

### Data Flow

```
Your Vault/
├── recordings/           ◄── You add audio files here
│   └── session-001.m4a
│
├── journals/             ◄── You write journal entries here
│   └── 2024-01-15.md
│
├── transcriptions/       ◄── transcribe skill outputs here
│   └── 2024-01-15-session-001.md
│
├── analysis/             ◄── analyze skill outputs here
│   └── 2024-01-15-session-001-analysis.md
│
├── progress/             ◄── progress skill outputs here
│   └── 2024-01-weekly-report.md
│
├── profile.md            ◄── insights skill maintains this
├── goals.md              ◄── You define therapy goals here
└── mindwork.yaml         ◄── Configuration file
```

---

## Example Queries

### Getting Started
```
"Transcribe my therapy session recording session-001.m4a"
"Analyze today's journal entry"
"Build my profile from all analyses"
```

### After a Session
```
"Transcribe and analyze my latest session"
"Give me a one-liner summary of today's session"
"What action items came out of this session?"
```

### Weekly Check-in
```
"Generate my weekly progress report"
"What patterns showed up this week?"
"Update my profile with this week's sessions"
```

### Monthly Review
```
"Compare my sessions from January vs March"
"Show me my highlights from this month"
"How has my catastrophizing changed over time?"
```

### Before Your Next Session
```
"Prep me for my session tomorrow"
"Summarize what to tell my therapist since last time"
"What were my action items and did I complete them?"
```

### Understanding Yourself
```
"What does my profile say about my triggers?"
"What coping strategies work best for me?"
"What are my core patterns?"
```

### Sharing with Others
```
"Summarize today's session for my partner"
"Create an update for my therapist about the past week"
"What can I share about my progress with my support system?"
```

### Goal Tracking
```
"How am I progressing on my goals?"
"Have I made progress on reducing anxiety?"
"What evidence is there that I'm improving at boundary-setting?"
```

---

## Installation

### Option 1: Clone and Add to Settings

```bash
git clone https://github.com/yourusername/mindwork.git ~/src/mindwork
```

Add to `~/.claude/settings.json`:
```json
{
  "plugins": ["~/src/mindwork"]
}
```

### Option 2: Use Directly

```bash
claude --plugin-dir ~/src/mindwork
```

## Setup

Build the Docker image for the transcription tool:

```bash
cd ~/src/mindwork/transcribe
docker build -t mindwork-transcribe .
```

Set your OpenAI API key (for transcription only):
```bash
export OPENAI_API_KEY="sk-..."
```

## Configuration

Create a `mindwork.yaml` file in your vault directory:

```yaml
vault: ~/Therapy

sources:
  recordings:
    paths: [recordings/]
  journals:
    paths: [journals/]

outputs:
  transcriptions: transcriptions/
  analysis: analysis/
  progress: progress/
```

See `config/mindwork.example.yaml` for all options.

**Config locations** (checked in order):
1. `./mindwork.yaml` (your vault directory)
2. `~/.config/mindwork/config.yaml`
3. `~/.mindwork.yaml`

---

## Skills Reference

### transcribe

Converts therapy session recordings into clean, formatted transcripts.

```
┌──────────────────────────────────────────────────────────────┐
│  Audio File  ───►  Chunk at Silence  ───►  Whisper API      │
│                                                ▼             │
│                         Formatted Transcript ◄───  GPT-4o   │
│                         (Me: / Therapist:)       (cleanup)  │
└──────────────────────────────────────────────────────────────┘
```

**Example queries:**
- `"Transcribe my therapy session recording session-001.m4a"`
- `"Transcribe the audio in recordings/"`

**Features:**
- Splits large audio at silence points (sentence boundaries)
- Transcribes using OpenAI Whisper API
- Formats as **Me:** / **Therapist:** dialogue
- Fixes grammar and transcription errors
- Translates to English (for non-English sessions)

**Supported formats:** mp3, mp4, m4a, wav, webm, ogg, flac

**Cost:** ~$0.30-0.50 per 50-minute session

---

### analyze

Deep analysis of a single session or journal entry.

```
┌──────────────────────────────────────────────────────────────┐
│  Transcript/Journal                                          │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ • Cognitive Patterns (catastrophizing, all-or-nothing) │ │
│  │ • Emotional Themes (anxiety, triggers, relief)         │ │
│  │ • Key Insights (realizations, connections)             │ │
│  │ • Progress Notes (compared to recent sessions)         │ │
│  │ • Suggested Focus Areas                                │ │
│  └─────────────────────────────────────────────────────────┘ │
│         │                                                    │
│         ▼                                                    │
│  analysis/2024-01-15-session-analysis.md                     │
└──────────────────────────────────────────────────────────────┘
```

**Example queries:**
- `"Analyze my therapy session from transcriptions/2024-01-15-session.md"`
- `"Analyze today's journal entry"`
- `"What patterns do you see in this session?"`

**Cognitive patterns detected:**
- All-or-nothing thinking
- Catastrophizing
- Mind reading
- Fortune telling
- Emotional reasoning
- Should statements
- Labeling
- Personalization
- And more...

---

### progress

Track changes over time, compare sessions, measure goal progress.

```
┌──────────────────────────────────────────────────────────────┐
│                     PROGRESS MODES                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Trend Tracking        Session Comparison      Goal Progress │
│  ───────────────       ──────────────────      ───────────── │
│  Pattern frequency     Side-by-side diff       Evidence of   │
│  over time             highlighting changes    progress       │
│                                                              │
│  Period Summaries                                            │
│  ────────────────                                            │
│  Weekly, monthly, quarterly reports                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Example queries:**
- `"Generate my weekly progress report"`
- `"Compare my first session with my most recent one"`
- `"How has my catastrophizing changed over the past month?"`
- `"How am I progressing on my goals?"`

**Goal tracking:** Create a `goals.md` file to define therapy goals. See `config/goals.example.md`.

---

### insights

Build and maintain a personal profile - a living document of self-knowledge.

```
┌──────────────────────────────────────────────────────────────┐
│                      profile.md                              │
│            (Updated incrementally over time)                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Core Patterns           │  Strengths                       │
│  ─────────────           │  ─────────                       │
│  • Thinking patterns     │  • Self-reflection capacity      │
│  • Emotional patterns    │  • Emotional vocabulary          │
│  • Triggers              │  • Growth commitment             │
│                          │                                   │
│  Coping Strategies       │  Growth Journey                  │
│  ─────────────────       │  ──────────────                  │
│  • What works for you    │  • Major realizations            │
│  • Techniques tried      │  • Skills developing             │
│                          │                                   │
│  Relationship Dynamics   │  Focus Areas                     │
│  ─────────────────────   │  ───────────                     │
│  • With authority        │  • Current therapeutic work      │
│  • With peers            │                                   │
│  • With self             │                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Example queries:**
- `"Build my profile from all analyses"`
- `"Update my profile with recent sessions"`
- `"What does my profile say about my triggers?"`
- `"What are my strengths according to my profile?"`

**Unique behavior:** Updates a single `profile.md` file rather than creating new files. Your profile grows richer over time.

---

### summary

Condense content for quick reference, different audiences, and session prep.

```
┌──────────────────────────────────────────────────────────────┐
│                      SUMMARY MODES                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  LENGTH OPTIONS          AUDIENCE OPTIONS                    │
│  ──────────────          ────────────────                    │
│  • One-liner             • For self (full detail)           │
│  • Paragraph             • For therapist (update format)    │
│  • Full page             • For sharing (non-clinical)       │
│                                                              │
│  SPECIAL MODES                                               │
│  ─────────────                                               │
│  • Action items (homework, next steps)                       │
│  • Highlights (breakthroughs, key quotes)                    │
│  • Session prep (recap + topics for next session)            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Example queries:**
- `"Give me a one-liner for today's session"`
- `"Summarize this for my partner"`
- `"What are my action items from recent sessions?"`
- `"Prep me for my session tomorrow"`
- `"Show me highlights from this month"`

---

## Typical Workflows

### New User: First Session

```
1. "Transcribe my first therapy session recording"
   → Creates: transcriptions/2024-01-15-session-001.md

2. "Analyze this session"
   → Creates: analysis/2024-01-15-session-001-analysis.md

3. "Build my initial profile"
   → Creates: profile.md

4. "What are my main patterns so far?"
   → Claude summarizes from the analysis
```

### Weekly Routine

```
Monday:    "Analyze my journal entry from yesterday"
Wednesday: "Transcribe and analyze yesterday's session"
Friday:    "Generate my weekly progress report"
           "Update my profile with this week's insights"
```

### Before Therapy Session

```
"Prep me for my session tomorrow"
→ Shows: Last session recap, journal highlights, suggested topics

"What action items did I have from last time?"
→ Shows: Checklist of homework and whether completed

"Create an update for my therapist"
→ Shows: What happened since last session, what worked, questions
```

### Monthly Review

```
"Monthly summary of my therapy progress"
"Compare this month to last month"
"How are my goals progressing?"
"Show me my breakthroughs from this month"
```

---

## All Skills

| Skill | Purpose | Key Differentiator |
|-------|---------|-------------------|
| `transcribe` | Audio → Text | Uses Docker + Whisper API |
| `analyze` | Deep pattern analysis | Per-session cognitive/emotional mapping |
| `progress` | Track changes over time | Trends, comparisons, goal tracking |
| `insights` | Build personal profile | Living document that evolves |
| `summary` | Quick condensed reference | Multiple lengths and audiences |

---

## Privacy Note

This tool processes sensitive personal data:

- **Transcription**: Audio chunking happens locally; transcription via OpenAI's Whisper API
- **Analysis/Progress/Insights/Summary**: Performed by Claude directly (no additional API calls beyond your Claude Code session)

No data is stored by this plugin. Your files stay in your vault.

Review OpenAI's data usage policies for their API and Anthropic's policies for Claude.

---

## Requirements

- Docker (for transcription)
- OpenAI API key (for transcription only)
- Claude Code CLI

---

## License

MIT

# Mindwork Configuration

Mindwork uses a simple YAML configuration file to understand your folder structure and preferences.

## Quick Start

1. Copy the example config to your therapy/journal vault:
   ```bash
   cp config/mindwork.example.yaml ~/Therapy/mindwork.yaml
   ```

2. Edit the file to match your folder structure:
   ```yaml
   vault: ~/Therapy

   sources:
     journals:
       sources:
         - path: ~/Obsidian/Personal/Daily Notes
           description: "Daily reflections"
   ```

3. Done! Mindwork skills will automatically use your config.

## Config File Locations

Mindwork checks for configuration in this order:

1. `./mindwork.yaml` - Your vault/project directory (recommended)
2. `~/.config/mindwork/config.yaml` - XDG standard location
3. `~/.mindwork.yaml` - Home directory fallback

## Minimal Configuration

The simplest config is just a vault path. Everything else uses sensible defaults:

```yaml
vault: ~/Therapy
```

With this config:
- Recordings expected in `~/Therapy/recordings/`
- Journals expected in `~/Therapy/journals/`
- Transcriptions saved to `~/Therapy/transcriptions/`
- Analysis saved to `~/Therapy/analysis/`

## Full Configuration Reference

```yaml
version: 1
vault: ~/Therapy

sources:
  recordings:
    paths:
      - recordings/                    # Relative to vault
      - ~/Voice Memos/Therapy          # Absolute path
    patterns: ["*.m4a", "*.mp3", "*.wav"]

  journals:
    sources:
      - path: journals/daily/
        description: "Daily reflections and mood check-ins"
      - path: journals/dreams/
        description: "Dream logs and interpretations"
    patterns: ["*.md", "*.txt"]

  transcriptions:
    paths: [transcriptions/]

outputs:
  transcriptions: transcriptions/
  analysis: analysis/

preferences:
  language: english
  date_format: "%Y-%m-%d"
  context_count: 5
```

## Configuration Options

### `vault`
Base directory for your mindwork data. All relative paths resolve from here.

### `sources`
Where to find input files.

**Recordings and transcriptions** support:
- `paths`: List of directories to search (relative to vault or absolute)
- `patterns`: Glob patterns for file matching

**Journals** use a richer structure with descriptions:
- `sources`: List of journal sources, each with:
  - `path`: Directory path (relative to vault or absolute)
  - `description`: Context for this journal type (used by skills for tailored analysis)
- `patterns`: Glob patterns for file matching

The description enables:
- Filtering by journal type: `"Analyze only my dream logs"`
- Context-aware analysis: dream logs focus on symbolism, gratitude logs on positive patterns
- Grouped reporting: `"3 daily entries, 2 dream logs this week"`

### `outputs`
Where to save processed files. Paths are relative to vault.

### `preferences`
| Option | Description | Default |
|--------|-------------|---------|
| `language` | Primary content language | `english` |
| `date_format` | Date format for filenames | `%Y-%m-%d` |
| `context_count` | Recent analyses to include for context | `5` |

## Example Setups

### Obsidian Vault Integration

Place `mindwork.yaml` in your Obsidian vault root:

```yaml
vault: ~/Obsidian/Personal

sources:
  journals:
    sources:
      - path: Daily Notes
        description: "Daily reflections and check-ins"
      - path: Reflections
        description: "Deeper self-reflection essays"
    patterns: ["*.md"]

  transcriptions:
    paths: [Therapy/Transcriptions]

outputs:
  transcriptions: Therapy/Transcriptions
  analysis: Therapy/Analysis
```

### Multiple Recording Sources

Combine synced voice memos with local recordings:

```yaml
vault: ~/Therapy

sources:
  recordings:
    paths:
      - recordings/
      - ~/Library/Mobile Documents/com~apple~VoiceMemos/Recordings
      - ~/Dropbox/Voice Memos
```

### Separate Vaults

Keep therapy and personal journals in different locations:

```yaml
vault: ~/Documents/Wellbeing

sources:
  journals:
    sources:
      - path: ~/Obsidian/Personal/Journals
        description: "Personal journal entries"
      - path: ~/Obsidian/Work/Reflections
        description: "Work-related reflections"

  recordings:
    paths:
      - ~/Therapy/Sessions
```

### Multiple Journal Types

Organize different journal practices:

```yaml
vault: ~/Therapy

sources:
  journals:
    sources:
      - path: journals/daily/
        description: "Daily mood check-ins and reflections"
      - path: journals/dreams/
        description: "Dream logs for interpretation"
      - path: journals/prompts/
        description: "Responses to therapy prompt cards"
      - path: journals/gratitude/
        description: "Gratitude practice entries"
      - path: journals/anxiety/
        description: "Anxiety tracking and triggers"
```

This enables queries like:
- `"Analyze my dream log from last night"`
- `"Show trends in my gratitude entries"`
- `"What patterns appear across my anxiety logs?"`

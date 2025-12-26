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
       paths:
         - ~/Obsidian/Personal/Daily Notes
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
    paths:
      - journals/
      - ~/Obsidian/Personal/Daily Notes
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
Where to find input files. Each source type supports:
- `paths`: List of directories to search (relative to vault or absolute)
- `patterns`: Glob patterns for file matching

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
    paths:
      - Daily Notes
      - Reflections
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
    paths:
      - ~/Obsidian/Personal/Journals
      - ~/Obsidian/Work/Reflections

  recordings:
    paths:
      - ~/Therapy/Sessions
```

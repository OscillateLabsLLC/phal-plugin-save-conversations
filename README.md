# SaveConversationsPlugin

[![Status: Active](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/OscillateLabsLLC/.github/blob/main/SUPPORT_STATUS.md)

An OVOS/Neon PHAL plugin that saves a transcript of your conversations in JSONL format.

These transcripts can be used to review your conversations, look for patterns, find opportunities to write new skills, or for any other purpose.

```python
self.bus.on("recognizer_loop:wakeword", self.record_message)
self.bus.on("recognizer_loop:utterance", self.record_message)
self.bus.on("speak", self.record_message)
```

## Configuration

OVOS `~/.config/mycroft/mycroft.conf`

```json
{
  "PHAL": {
    "phal-plugin-save-conversations": {
      "save_path": "/home/ovos/.cache/transcripts"
    }
  }
}
```

Neon `~/.config/neon/neon.yaml`

```yaml
PHAL:
  phal-plugin-save-conversations:
    save_path: "/home/neon/.cache/transcripts"
```

## Credits

- Mike Gray (@mikejgray)

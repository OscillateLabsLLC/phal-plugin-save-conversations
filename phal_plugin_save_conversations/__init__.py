import threading
from datetime import datetime, timezone
from os import path
from pathlib import Path

import orjson
from ovos_bus_client import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG
from ovos_utils.xdg_utils import xdg_cache_home


class MessageLogger:
    """Logs Message objects to JSONL files with timestamps."""

    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = None
        self.lock = threading.Lock()
        self.rotate_file()

    def rotate_file(self):
        """Creates a new log file for each day."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.current_file = self.log_dir / f"messages_{date_str}.jsonl"

    def log_message(self, message: "Message"):
        """Logs a message with timestamp to the current JSONL file."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create the log entry
        log_entry = {
            "timestamp": timestamp,
            "msg_type": message.msg_type,
            "data": message.data,
            "context": message.context,
        }
        json_str = orjson.dumps(log_entry).decode("utf-8")

        with self.lock:
            # Check if we need to rotate to a new day's file
            current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if not self.current_file:
                self.rotate_file()
            if not self.current_file.name.endswith(f"{current_date}.jsonl"):  # type: ignore
                self.rotate_file()

            try:
                # Append to file
                with open(self.current_file, "a", encoding="utf-8") as f:  # type: ignore
                    f.write(json_str + "\n")
            except Exception:
                LOG.exception("Failed to write message to %s", self.current_file)
                LOG.debug(json_str)


class SaveConversationsPlugin(PHALPlugin):
    """A PHAL plugin that saves conversations to a file."""

    def __init__(self, *args, bus=None, **kwargs):
        super().__init__(*args, bus=bus, **kwargs)
        self.bus.on("recognizer_loop:wakeword", self.record_message)
        self.bus.on("recognizer_loop:utterance", self.record_message)
        self.bus.on("speak", self.record_message)
        self.message_logger = MessageLogger(log_dir=self.save_path)

    @property
    def save_path(self):
        """The path to save the conversations to."""
        return self.config.get("save_path", path.join(xdg_cache_home(), "transcripts"))

    def record_message(self, message: Message):
        """Save the conversation to a file."""
        self.message_logger.log_message(message)

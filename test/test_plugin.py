from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import mock_open, patch

import orjson
import pytest
from ovos_bus_client import Message
from ovos_utils.messagebus import FakeBus

from phal_plugin_save_conversations import MessageLogger, SaveConversationsPlugin


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture to provide a temporary directory."""
    return tmp_path


@pytest.fixture
def message_logger(temp_dir):
    """Fixture to provide a MessageLogger instance."""
    return MessageLogger(str(temp_dir))


@pytest.fixture
def sample_message():
    """Fixture to provide a sample Message object."""
    return Message(msg_type="speak", data={"utterance": "Hello world"}, context={"user": "test_user"})


@pytest.fixture
def fake_bus():
    """Fixture to provide a fake message bus."""
    return FakeBus()


class TestMessageLogger:
    def test_init(self, temp_dir):
        """Test MessageLogger initialization."""
        logger = MessageLogger(str(temp_dir))
        assert logger.log_dir == Path(temp_dir)
        assert logger.log_dir.exists()

    def test_rotate_file(self, message_logger):
        """Test file rotation."""
        message_logger.rotate_file()
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        expected_filename = f"messages_{current_date}.jsonl"
        assert message_logger.current_file.name == expected_filename

    def test_log_message(self, message_logger, sample_message, temp_dir):
        """Test logging a message."""
        message_logger.log_message(sample_message)

        # Get the current log file
        log_files = list(temp_dir.glob("messages_*.jsonl"))
        assert len(log_files) == 1

        # Read and verify the log content
        with open(log_files[0], "r") as f:
            log_entry = orjson.loads(f.readline())
            assert log_entry["msg_type"] == sample_message.msg_type
            assert log_entry["data"] == sample_message.data
            assert log_entry["context"] == sample_message.context
            assert "timestamp" in log_entry

    def test_log_message_file_error(self, message_logger, sample_message):
        """Test handling of file write errors."""
        # Mock open to raise an IOError
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Test error")

            # This should not raise an exception
            message_logger.log_message(sample_message)

    def test_concurrent_logging(self, message_logger, sample_message):
        """Test concurrent message logging."""
        import queue
        import threading

        # Queue to collect any exceptions that occur in threads
        errors = queue.Queue()

        def log_message_wrapper():
            try:
                message_logger.log_message(sample_message)
            except Exception as e:
                errors.put(e)

        # Create and start multiple threads
        threads = [threading.Thread(target=log_message_wrapper) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Check if any errors occurred
        assert errors.empty(), f"Concurrent logging produced errors: {list(errors.queue)}"


class TestSaveConversationsPlugin:
    def test_init(self, fake_bus, temp_dir):
        """Test plugin initialization."""
        config = {"save_path": str(temp_dir)}
        plugin = SaveConversationsPlugin(bus=fake_bus, config=config)

        assert plugin.save_path == str(temp_dir)
        assert isinstance(plugin.message_logger, MessageLogger)

    def test_record_message(self, fake_bus, temp_dir):
        """Test message recording."""
        config = {"save_path": str(temp_dir)}
        plugin = SaveConversationsPlugin(bus=fake_bus, config=config)

        test_message = Message(msg_type="speak", data={"utterance": "Test message"}, context={"user": "test_user"})

        plugin.record_message(test_message)

        # Verify the message was logged
        log_files = list(Path(temp_dir).glob("messages_*.jsonl"))
        assert len(log_files) == 1

        with open(log_files[0], "r") as f:
            log_entry = orjson.loads(f.readline())
            assert log_entry["msg_type"] == test_message.msg_type
            assert log_entry["data"] == test_message.data

    def test_message_bus_integration(self, fake_bus, temp_dir):
        """Test integration with message bus events."""
        config = {"save_path": str(temp_dir)}
        plugin = SaveConversationsPlugin(bus=fake_bus, config=config)

        # Emit test messages on the bus
        test_messages = [
            Message("recognizer_loop:wakeword", {"wake_word": "hey mycroft"}),
            Message("recognizer_loop:utterance", {"utterances": ["what's the weather"]}),
            Message("speak", {"utterance": "It's sunny today"}),
        ]

        for msg in test_messages:
            fake_bus.emit(msg)

        # Give a small delay for processing
        import time

        time.sleep(0.1)

        # Verify messages were logged
        log_files = list(Path(temp_dir).glob("messages_*.jsonl"))
        assert len(log_files) == 1

        with open(log_files[0], "r") as f:
            logged_messages = [orjson.loads(line) for line in f]
            assert len(logged_messages) == len(test_messages)

            for logged, original in zip(logged_messages, test_messages):
                assert logged["msg_type"] == original.msg_type
                assert logged["data"] == original.data


if __name__ == "__main__":
    pytest.main([__file__])

# tests/test_integration.py
import logging


from omni_logger import set_logger, get_logger
from omni_logger.config import FileHandlerConfig, LogConfig


def test_get_logger_returns_same_as_logging_getLogger():
    """Verify get_logger() is symmetric with logging.getLogger()."""
    config = LogConfig()
    set_logger("test_app", config)

    logger1 = get_logger("test_app")
    logger2 = logging.getLogger("test_app")

    assert logger1 is logger2


def test_full_logging_flow_console_and_file(tmp_path, caplog):
    """Test end-to-end logging with console and file handlers."""
    config = LogConfig(
        handlers=["console", "file"],
        file=FileHandlerConfig(log_dir=tmp_path)
    )
    logger = set_logger("integration_test", config)

    with caplog.at_level(logging.INFO):
        logger.info("Test message")

    # Verify console captured the log
    assert any("Test message" in record.message for record in caplog.records)

    # Verify file captured the log
    log_file = tmp_path / "integration_test.log"
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content


def test_logger_reconfiguration():
    """Test that calling set_logger() again replaces configuration."""
    config1 = LogConfig(handlers=["console"])
    logger1 = set_logger("reconfig_test", config1)
    assert len(logger1.handlers) == 1

    config2 = LogConfig(handlers=["console", "file"])
    logger2 = set_logger("reconfig_test", config2)
    assert logger1 is logger2  # Same instance
    assert len(logger2.handlers) == 2  # Reconfigured


def test_dingtalk_handler_integration(mock_requests_post, mock_dingtalk_env):
    """Test Dingtalk handler sends ERROR level logs."""
    config = LogConfig(handlers=["dingtalk"])
    logger = set_logger("dingtalk_test", config)

    logger.error("Critical error occurred")

    # Verify Dingtalk was called
    mock_requests_post.assert_called_once()


def test_dingtalk_handler_skips_info_logs(mock_requests_post, mock_dingtalk_env):
    """Test Dingtalk handler ignores INFO level logs."""
    config = LogConfig(handlers=["dingtalk"])
    logger = set_logger("dingtalk_test", config)

    logger.info("This should not trigger Dingtalk")

    # Verify Dingtalk was NOT called
    mock_requests_post.assert_not_called()

# tests/test_dingtalk_handler.py
import logging
import os


from omni_logger.handlers.dingtalk import DingtalkErrorHandler


def test_dingtalk_handler_filters_below_error():
    handler = DingtalkErrorHandler()
    assert handler.level >= logging.ERROR


def test_dingtalk_handler_emits_error_records(mock_requests_post, mock_dingtalk_env):
    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Test error",
        args=(),
        exc_info=None
    )
    handler.emit(record)
    mock_requests_post.assert_called_once()


def test_dingtalk_handler_ignores_info_records(mock_requests_post):
    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test info",
        args=(),
        exc_info=None
    )
    handler.emit(record)
    mock_requests_post.assert_not_called()


def test_dingtalk_handler_missing_env_vars_logs_warning(capfd):
    # Clear env vars
    os.environ.pop("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN", None)
    os.environ.pop("ALGO_SERVICES_DINGTALK_SIGNATURE", None)

    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Test error",
        args=(),
        exc_info=None
    )
    handler.emit(record)

    captured = capfd.readouterr()
    assert "DingtalkErrorHandler" in captured.err


def test_dingtalk_handler_send_failure_prints_to_stderr(capfd, mock_requests_post):
    os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = "test_token"
    os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = "test_secret"

    mock_requests_post.side_effect = Exception("Network error")

    handler = DingtalkErrorHandler()
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Test error",
        args=(),
        exc_info=None
    )
    handler.emit(record)

    captured = capfd.readouterr()
    assert "Failed" in captured.err

# tests/conftest.py
import os
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_log_dir(tmp_path):
    """Temporary log directory for testing."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


@pytest.fixture
def mock_dingtalk_env():
    """Set up Dingtalk environment variables for testing."""
    original_token = os.environ.get("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN")
    original_signature = os.environ.get("ALGO_SERVICES_DINGTALK_SIGNATURE")

    os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = "test_token"
    os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = "test_secret"

    yield

    if original_token is not None:
        os.environ["ALGO_SERVICES_DINGTALK_ACCESS_TOKEN"] = original_token
    else:
        os.environ.pop("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN", None)

    if original_signature is not None:
        os.environ["ALGO_SERVICES_DINGTALK_SIGNATURE"] = original_signature
    else:
        os.environ.pop("ALGO_SERVICES_DINGTALK_SIGNATURE", None)


@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mock requests.post for Dingtalk tests."""
    mock = MagicMock()
    monkeypatch.setattr("requests.post", mock)
    return mock

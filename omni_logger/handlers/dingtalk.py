# omni_logger/handlers/dingtalk.py
"""Dingtalk error handler for logging notifications."""
import base64
import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import quote_plus

import requests


class DingtalkErrorHandler(logging.Handler):
    """Send ERROR and above log records to Dingtalk webhook."""

    _access_token: str
    _signature: str
    _url_body: str

    def __init__(self):
        super().__init__()
        self._access_token = os.getenv("ALGO_SERVICES_DINGTALK_ACCESS_TOKEN", "")
        self._signature = os.getenv("ALGO_SERVICES_DINGTALK_SIGNATURE", "")
        self._url_body = "https://oapi.dingtalk.com/robot/send"

        # Set level to ERROR by default
        self.setLevel(logging.ERROR)

        # Add a default formatter to ensure asctime is available
        self.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    def _generate_url_with_timestamp(self) -> str:
        """Generate signed URL with timestamp."""
        timestamp = str(round(time.time() * 1000))
        hmac_code = hmac.new(
            self._signature.encode("utf-8"),
            f"{timestamp}\n{self._signature}".encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        sign = quote_plus(base64.b64encode(hmac_code).decode("utf-8"))
        return self._url_body + f"?access_token={self._access_token}&timestamp={timestamp}&sign={sign}"

    def emit(self, record: logging.LogRecord):
        """Emit a log record if level is ERROR or above.

        Missing credentials or send failures are logged to stderr but don't crash.
        """
        if record.levelno < logging.ERROR:
            return

        if not self._access_token or not self._signature:
            print("DingtalkErrorHandler: Missing ALGO_SERVICES_DINGTALK_ACCESS_TOKEN or ALGO_SERVICES_DINGTALK_SIGNATURE env vars", file=__import__("sys").stderr)
            return

        self.format(record)
        self.send(record)

    def send(self, record: logging.LogRecord):
        """Send log record to Dingtalk.

        Send failures are printed to stderr but don't propagate.
        """
        data = {
            "msgtype": "text",
            "text": {
                "content": {
                    "asctime": record.asctime,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "filename": record.filename,
                    "lineno": record.lineno,
                }
            },
            "at": {
                "atMobiles": [],
                "isAtAll": False
            }
        }

        try:
            requests.post(
                url=self._generate_url_with_timestamp(),
                headers={"Content-Type": "application/json"},
                data=json.dumps(data, ensure_ascii=False)
            )
        except Exception as e:
            print(f"DingtalkErrorHandler.send() Failed: {e}", file=__import__("sys").stderr)

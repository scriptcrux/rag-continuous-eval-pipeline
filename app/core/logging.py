"""Structured logging configuration for CloudPulse RAG engine."""

import logging
import sys
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_payload["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_payload["duration_ms"] = record.duration_ms
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_payload)


def get_logger(name: str = "cloudpulse") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


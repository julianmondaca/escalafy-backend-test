"""
Configuration for structured JSON logging.
"""
import logging
import json
from datetime import datetime, timezone
import sys

class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs as JSON strings.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "component": getattr(record, "component", "global"),
        }
        return json.dumps(log_obj)

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger with the custom JSON formatter.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    return logger

"""Logging configuration for the application."""

import logging
import sys
from datetime import datetime


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure application logging."""
    
    # Create logger
    logger = logging.getLogger("rag_app")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger


logger = setup_logging()
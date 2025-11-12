

# ============================================
# astro-service/app/utils/logger.py
# ============================================
"""
Logging configuration and utilities.
Provides structured logging with JSON support.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import json


# ============================================
# Log Levels
# ============================================

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


# ============================================
# Custom JSON Formatter
# ============================================

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def __init__(self, include_extra: bool = True):
        """
        Initialize JSON formatter.
        
        Args:
            include_extra: Include extra fields in log record
        """
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if self.include_extra:
            # Get all custom attributes
            extra_fields = {
                key: value
                for key, value in record.__dict__.items()
                if key not in [
                    'name', 'msg', 'args', 'created', 'filename', 'funcName',
                    'levelname', 'levelno', 'lineno', 'module', 'msecs',
                    'message', 'pathname', 'process', 'processName',
                    'relativeCreated', 'thread', 'threadName', 'exc_info',
                    'exc_text', 'stack_info'
                ]
            }
            if extra_fields:
                log_data["extra"] = extra_fields
        
        return json.dumps(log_data)


# ============================================
# Custom Colored Formatter (Console)
# ============================================

class ColoredFormatter(logging.Formatter):
    """Add colors to console logs for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        # Get color for level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build log line
        log_line = (
            f"{color}[{timestamp}] "
            f"{record.levelname:8s}{reset} "
            f"{record.name}: {record.getMessage()}"
        )
        
        # Add exception if present
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line


# ============================================
# Logger Setup
# ============================================

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = False,
    include_extra: bool = True
) -> logging.Logger:
    """
    Set up application logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None = console only)
        json_logs: Use JSON format for logs
        include_extra: Include extra fields in JSON logs
    
    Returns:
        Configured logger instance
    """
    # Get log level
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if json_logs:
        console_handler.setFormatter(JSONFormatter(include_extra=include_extra))
    else:
        console_handler.setFormatter(ColoredFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Create log directory if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter(include_extra=include_extra))
        root_logger.addHandler(file_handler)
        
        root_logger.info(f"Logging to file: {log_file}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for specific module.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# ============================================
# Context Logger
# ============================================

class LogContext:
    """Add contextual information to all logs within scope."""
    
    def __init__(self, logger: logging.Logger, **context):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            **context: Context fields to add to logs
        
        Example:
            with LogContext(logger, request_id="abc123", user_id=42):
                logger.info("Processing request")
                # Logs will include request_id and user_id
        """
        self.logger = logger
        self.context = context
        self.old_factory = None
    
    def __enter__(self):
        """Enter context."""
        # Save old factory
        self.old_factory = logging.getLogRecordFactory()
        
        # Create new factory that adds context
        context = self.context
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        # Restore old factory
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


# ============================================
# Performance Logger
# ============================================

class PerformanceLogger:
    """Log function execution time."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        """
        Initialize performance logger.
        
        Args:
            logger: Logger instance
            operation: Operation name
        
        Example:
            with PerformanceLogger(logger, "predict_visibility"):
                result = await predict()
            # Logs: "predict_visibility completed in 1.23s"
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log elapsed time."""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            if exc_type:
                self.logger.error(
                    f"{self.operation} failed after {elapsed:.3f}s",
                    exc_info=(exc_type, exc_val, exc_tb)
                )
            else:
                self.logger.info(f"{self.operation} completed in {elapsed:.3f}s")


# ============================================
# Utility Functions
# ============================================

def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with arguments.
    
    Example:
        @log_function_call(logger)
        async def predict_visibility(satellite, lat, lng):
            ...
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Log function call
            logger.debug(
                f"Calling {func.__name__}",
                extra={
                    "function": func.__name__,
                    "args": str(args[1:]),  # Skip self
                    "kwargs": str(kwargs)
                }
            )
            
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(
                    f"{func.__name__} raised exception: {e}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_exception(logger: logging.Logger, message: str = "Exception occurred"):
    """
    Context manager to log exceptions.
    
    Example:
        with log_exception(logger, "Processing request"):
            risky_operation()
    """
    class ExceptionLogger:
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                logger.error(message, exc_info=(exc_type, exc_val, exc_tb))
            return False  # Don't suppress exception
    
    return ExceptionLogger()


# ============================================
# Initialize Default Logger
# ============================================

def init_logger_from_env():
    """Initialize logger from environment variables."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
    json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"
    
    return setup_logging(
        level=log_level,
        log_file=log_file,
        json_logs=json_logs
    )
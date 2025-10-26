"""
Logging utility for AURA project.
Provides centralized logging configuration with console and file handlers.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class AURALogger:
    """Centralized logger for the AURA project."""
    
    _loggers = {}
    _log_dir = Path("logs")
    _initialized = False
    
    @classmethod
    def setup(cls, log_level: str = "INFO", log_to_file: bool = True):
        """
        Setup the logging configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file in addition to console
        """
        if cls._initialized:
            return
        
        # Create logs directory if it doesn't exist
        if log_to_file:
            cls._log_dir.mkdir(exist_ok=True)
        
        cls._log_level = getattr(logging, log_level.upper(), logging.INFO)
        cls._log_to_file = log_to_file
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger with the specified name.
        
        Args:
            name: Name of the logger (typically __name__ of the module)
            
        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.setup()
        
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(cls._log_level)
        logger.propagate = False
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Console handler with color formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(cls._log_level)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (if enabled)
        if cls._log_to_file:
            log_filename = cls._log_dir / f"aura_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(cls._log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format the log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Color the level name
        record.levelname = f"{log_color}{record.levelname}{reset}"
        
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return AURALogger.get_logger(name)

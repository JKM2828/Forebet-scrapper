"""
Moduł logowania z kolorowymi logami i rotacją plików.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

from ..config import Settings


class Logger:
    """Zarządzanie logowaniem aplikacji."""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, log_level: Optional[str] = None) -> logging.Logger:
        """
        Pobiera lub tworzy logger o podanej nazwie.
        
        Args:
            name: Nazwa loggera (zwykle __name__)
            log_level: Poziom logowania (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            Skonfigurowany logger
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Ustaw poziom logowania
        level = log_level or Settings.LOG_LEVEL
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Nie propaguj do root logger
        logger.propagate = False
        
        # Usuń istniejące handlery
        logger.handlers.clear()
        
        # Dodaj handlery
        logger.addHandler(cls._get_console_handler())
        logger.addHandler(cls._get_file_handler())
        
        cls._loggers[name] = logger
        return logger
    
    @staticmethod
    def _get_console_handler() -> logging.Handler:
        """Tworzy handler dla konsoli z kolorowaniem."""
        console_handler = logging.StreamHandler(sys.stdout)
        
        if COLORLOG_AVAILABLE:
            # Kolorowy format
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt=Settings.LOG_DATE_FORMAT,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
        else:
            # Standardowy format bez kolorów
            formatter = logging.Formatter(
                Settings.LOG_FORMAT,
                datefmt=Settings.LOG_DATE_FORMAT
            )
        
        console_handler.setFormatter(formatter)
        return console_handler
    
    @staticmethod
    def _get_file_handler() -> logging.Handler:
        """Tworzy handler dla pliku z rotacją."""
        # Upewnij się, że katalog logów istnieje
        log_file = Settings.LOGS_DIR / "forebet_scraper.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (max 10MB, 5 backup files)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            Settings.LOG_FORMAT,
            datefmt=Settings.LOG_DATE_FORMAT
        )
        
        file_handler.setFormatter(formatter)
        return file_handler
    
    @staticmethod
    def _get_error_file_handler() -> logging.Handler:
        """Tworzy handler dla błędów (ERROR i CRITICAL tylko)."""
        error_log_file = Settings.LOGS_DIR / "forebet_scraper_errors.log"
        error_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            Settings.LOG_FORMAT,
            datefmt=Settings.LOG_DATE_FORMAT
        )
        
        error_handler.setFormatter(formatter)
        return error_handler
    
    @classmethod
    def setup_root_logger(cls):
        """Konfiguruje główny root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.handlers.clear()
        
        # Dodaj handlery
        root_logger.addHandler(cls._get_console_handler())
        root_logger.addHandler(cls._get_file_handler())
        root_logger.addHandler(cls._get_error_file_handler())


# Helper function dla szybkiego dostępu
def get_logger(name: str) -> logging.Logger:
    """
    Skrót do pobierania loggera.
    
    Usage:
        from src.data_management.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Wiadomość")
    """
    return Logger.get_logger(name)

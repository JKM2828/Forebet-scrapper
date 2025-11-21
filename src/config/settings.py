"""
Moduł konfiguracji - globalne ustawienia aplikacji.
"""
from enum import Enum
from pathlib import Path
from typing import List


class Sport(str, Enum):
    """Wspierane sporty na Forebet."""
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    VOLLEYBALL = "volleyball"
    HOCKEY = "hockey"
    HANDBALL = "handball"
    AMERICAN_FOOTBALL = "american-football"
    BASEBALL = "baseball"
    RUGBY = "rugby"
    CRICKET = "cricket"


class Settings:
    """Główne ustawienia aplikacji."""
    
    # Ścieżki projektu
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / "cache"
    
    # Forebet Configuration
    FOREBET_BASE_URL = "https://www.forebet.com/pl"
    FOREBET_TIMEOUT = 30
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Scraper Configuration
    NOTIFICATION_THRESHOLD = 60  # Minimalny % przewagi matematycznej
    MATCHES_TO_ANALYZE = 6  # Liczba ostatnich meczów do analizy formy
    H2H_MATCHES_TO_ANALYZE = 10  # Liczba meczów H2H do analizy
    H2H_MIN_WIN_RATE = 0.60  # Minimalny win rate w H2H (60%)
    
    # Cache Configuration
    CACHE_DURATION = 3600  # 1 godzina w sekundach
    
    # Rate Limiting
    REQUEST_DELAY = 2  # Opóźnienie między requestami (sekundy)
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # Początkowe opóźnienie retry (exponential backoff)
    
    # Browser Configuration (Selenium)
    HEADLESS_BROWSER = True
    BROWSER_TIMEOUT = 30
    IMPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 30
    
    # Email Configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USE_TLS = True
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Wspierane sporty (priorytet)
    SUPPORTED_SPORTS: List[Sport] = [
        Sport.FOOTBALL,
        Sport.BASKETBALL,
        Sport.VOLLEYBALL,
        Sport.HOCKEY,
        Sport.HANDBALL,
    ]
    
    # URL patterns dla sportów (polskie URL Forebet.com)
    SPORT_URL_PATTERNS = {
        Sport.FOOTBALL: "prognozy-piłkarskie-na-dziś",
        Sport.BASKETBALL: "basketball/prognozy-na-dzis",  # TODO: sprawdzić poprawny URL
        Sport.VOLLEYBALL: "volleyball/prognozy-na-dzis",  # TODO: sprawdzić poprawny URL
        Sport.HOCKEY: "hockey/prognozy-na-dzis",          # TODO: sprawdzić poprawny URL
        Sport.HANDBALL: "handball/prognozy-na-dzis",      # TODO: sprawdzić poprawny URL
        Sport.AMERICAN_FOOTBALL: "american-football/prognozy-na-dzis",
        Sport.BASEBALL: "baseball/prognozy-na-dzis",
        Sport.RUGBY: "rugby/prognozy-na-dzis",
        Sport.CRICKET: "cricket/prognozy-na-dzis",
    }
    
    @classmethod
    def get_sport_url(cls, sport: Sport) -> str:
        """Zwraca pełny URL dla danego sportu."""
        pattern = cls.SPORT_URL_PATTERNS.get(sport)
        if not pattern:
            raise ValueError(f"Nieobsługiwany sport: {sport}")
        return f"{cls.FOREBET_BASE_URL}/{pattern}"
    
    @classmethod
    def ensure_directories(cls):
        """Tworzy wymagane katalogi jeśli nie istnieją."""
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Upewnij się, że katalogi istnieją przy imporcie
Settings.ensure_directories()

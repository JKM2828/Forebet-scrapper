"""
Moduł zarządzania sekretami i zmiennymi środowiskowymi.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class SecretsManager:
    """Zarządzanie sekretami i zmiennymi środowiskowymi."""
    
    def __init__(self):
        """Inicjalizacja i wczytanie zmiennych środowiskowych."""
        # Znajdź plik .env
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        
        # Wczytaj zmienne środowiskowe
        if env_path.exists():
            load_dotenv(env_path)
        else:
            print(f"⚠️  Uwaga: Plik .env nie został znaleziony: {env_path}")
            print("⚠️  Używam zmiennych środowiskowych systemowych.")
    
    @staticmethod
    def get(key: str, default: Optional[str] = None, required: bool = False) -> str:
        """
        Pobiera wartość zmiennej środowiskowej.
        
        Args:
            key: Nazwa zmiennej
            default: Wartość domyślna jeśli zmienna nie istnieje
            required: Czy zmienna jest wymagana (rzuca wyjątek jeśli brak)
        
        Returns:
            Wartość zmiennej lub default (zawsze string)
        
        Raises:
            ValueError: Jeśli zmienna wymagana nie istnieje
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(
                f"Wymagana zmienna środowiskowa '{key}' nie została ustawiona. "
                f"Sprawdź plik .env lub zmienne środowiskowe systemu."
            )
        
        return value or default or ""
    
    @staticmethod
    def get_int(key: str, default: int = 0, required: bool = False) -> int:
        """Pobiera wartość zmiennej jako integer."""
        value = SecretsManager.get(key, str(default), required)
        
        if not value:
            return default
        
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Zmienna '{key}' musi być liczbą całkowitą, otrzymano: {value}")
    
    @staticmethod
    def get_bool(key: str, default: bool = False, required: bool = False) -> bool:
        """Pobiera wartość zmiennej jako boolean."""
        value = SecretsManager.get(key, str(default), required)
        
        if not value:
            return default
        
        return value.lower() in ("true", "1", "yes", "on")
    
    @staticmethod
    def validate_required_secrets():
        """
        Waliduje czy wszystkie wymagane sekrety są ustawione.
        
        Raises:
            ValueError: Jeśli brakuje wymaganych sekretów
        """
        required_secrets = [
            "GMAIL_USER",
            "GMAIL_PASSWORD",
            "RECIPIENT_EMAIL",
        ]
        
        missing = []
        for secret in required_secrets:
            if not SecretsManager.get(secret):
                missing.append(secret)
        
        if missing:
            raise ValueError(
                f"Brakujące wymagane zmienne środowiskowe: {', '.join(missing)}\n"
                f"Sprawdź plik .env.example i utwórz plik .env z odpowiednimi wartościami."
            )
    
    # Gmail Configuration
    @property
    def gmail_user(self) -> str:
        """Email użytkownika Gmail."""
        return self.get("GMAIL_USER", required=True)
    
    @property
    def gmail_password(self) -> str:
        """App Password Gmail."""
        return self.get("GMAIL_PASSWORD", required=True)
    
    @property
    def recipient_email(self) -> str:
        """Email odbiorcy powiadomień."""
        return self.get("RECIPIENT_EMAIL", required=True)
    
    # Forebet Configuration
    @property
    def forebet_base_url(self) -> str:
        """Bazowy URL Forebet."""
        return self.get("FOREBET_BASE_URL", "https://www.forebet.com/pl")
    
    @property
    def forebet_timeout(self) -> int:
        """Timeout dla requestów Forebet."""
        return self.get_int("FOREBET_TIMEOUT", 30)
    
    # Scraper Configuration
    @property
    def notification_threshold(self) -> int:
        """Minimalny próg przewagi matematycznej (%)."""
        return self.get_int("NOTIFICATION_THRESHOLD", 60)
    
    @property
    def matches_to_analyze(self) -> int:
        """Liczba ostatnich meczów do analizy formy."""
        return self.get_int("MATCHES_TO_ANALYZE", 6)
    
    @property
    def h2h_matches_to_analyze(self) -> int:
        """Liczba meczów H2H do analizy."""
        return self.get_int("H2H_MATCHES_TO_ANALYZE", 10)
    
    @property
    def cache_duration(self) -> int:
        """Czas życia cache w sekundach."""
        return self.get_int("CACHE_DURATION", 3600)
    
    # Logging Configuration
    @property
    def log_level(self) -> str:
        """Poziom logowania."""
        return self.get("LOG_LEVEL", "INFO")
    
    @property
    def log_file(self) -> str:
        """Ścieżka do pliku logów."""
        return self.get("LOG_FILE", "logs/forebet_scraper.log")
    
    # Browser Configuration
    @property
    def headless_browser(self) -> bool:
        """Czy uruchamiać przeglądarkę w trybie headless."""
        return self.get_bool("HEADLESS_BROWSER", True)
    
    @property
    def browser_timeout(self) -> int:
        """Timeout dla przeglądarki Selenium."""
        return self.get_int("BROWSER_TIMEOUT", 30)


# Globalny singleton
secrets = SecretsManager()

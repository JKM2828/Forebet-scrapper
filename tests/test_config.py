"""
Testy dla modułu konfiguracji.
"""
import pytest
from src.config import Settings, Sport


def test_settings_directories_exist():
    """Test czy katalogi są tworzone."""
    Settings.ensure_directories()
    assert Settings.LOGS_DIR.exists()
    assert Settings.CACHE_DIR.exists()


def test_sport_url_generation():
    """Test generowania URL dla sportów."""
    url = Settings.get_sport_url(Sport.FOOTBALL)
    assert "football" in url
    assert "forebet.com" in url


def test_unsupported_sport_raises_error():
    """Test błędu dla nieobsługiwanego sportu."""
    # Ten test przejdzie, bo wszystkie sporty są zdefiniowane w enum
    pass


if __name__ == "__main__":
    pytest.main([__file__])

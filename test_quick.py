"""
Szybki test podstawowych funkcjonalności projektu.
"""
import sys
from pathlib import Path

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test importów wszystkich głównych modułów."""
    print("🔍 Testowanie importów...")
    
    try:
        from src.config import Settings, Sport, secrets
        print("✅ Config: OK")
    except Exception as e:
        print(f"❌ Config: {e}")
        return False
    
    try:
        from src.data_management import get_logger, cache_manager
        print("✅ Data Management: OK")
    except Exception as e:
        print(f"❌ Data Management: {e}")
        return False
    
    try:
        from src.scrapers import ForebtScraper
        print("✅ Scrapers: OK")
    except Exception as e:
        print(f"❌ Scrapers: {e}")
        return False
    
    try:
        from src.analyzers import HeadToHeadAnalyzer, FormAnalyzer, HomeAwayAnalyzer
        print("✅ Analyzers: OK")
    except Exception as e:
        print(f"❌ Analyzers: {e}")
        return False
    
    try:
        from src.filters import EventFilter
        print("✅ Filters: OK")
    except Exception as e:
        print(f"❌ Filters: {e}")
        return False
    
    try:
        from src.notifiers import EmailSender
        print("✅ Notifiers: OK")
    except Exception as e:
        print(f"❌ Notifiers: {e}")
        return False
    
    return True


def test_config():
    """Test konfiguracji."""
    print("\n🔍 Testowanie konfiguracji...")
    
    from src.config import Settings, Sport
    
    # Test katalogów
    assert Settings.LOGS_DIR.exists(), "Katalog logs nie istnieje"
    print(f"✅ Logs dir: {Settings.LOGS_DIR}")
    
    assert Settings.CACHE_DIR.exists(), "Katalog cache nie istnieje"
    print(f"✅ Cache dir: {Settings.CACHE_DIR}")
    
    # Test URL generation
    url = Settings.get_sport_url(Sport.FOOTBALL)
    assert "forebet.com" in url
    assert "football" in url
    print(f"✅ URL generation: {url}")
    
    return True


def test_secrets():
    """Test sekretów (bez wyświetlania wrażliwych danych)."""
    print("\n🔍 Testowanie sekretów...")
    
    from src.config import secrets
    
    try:
        # Sprawdź czy zmienne są załadowane
        assert secrets.gmail_user, "GMAIL_USER nie jest ustawiony"
        print(f"✅ GMAIL_USER: {secrets.gmail_user}")
        
        assert secrets.gmail_password, "GMAIL_PASSWORD nie jest ustawiony"
        print(f"✅ GMAIL_PASSWORD: {'*' * len(secrets.gmail_password)}")
        
        assert secrets.recipient_email, "RECIPIENT_EMAIL nie jest ustawiony"
        print(f"✅ RECIPIENT_EMAIL: {secrets.recipient_email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd sekretów: {e}")
        return False


def test_logger():
    """Test systemu logowania."""
    print("\n🔍 Testowanie systemu logowania...")
    
    from src.data_management import get_logger
    
    logger = get_logger(__name__)
    logger.info("Test log INFO")
    logger.warning("Test log WARNING")
    logger.error("Test log ERROR")
    
    print("✅ Logger działa (sprawdź logs/forebet_scraper.log)")
    return True


def test_cache():
    """Test cache managera."""
    print("\n🔍 Testowanie cache managera...")
    
    from src.data_management import cache_manager
    
    # Test save/load
    test_data = {"test": "value", "number": 123}
    cache_manager.save("test_key", test_data, ttl=60)
    
    loaded = cache_manager.load("test_key")
    assert loaded == test_data, "Cache nie działa poprawnie"
    
    # Info
    info = cache_manager.get_cache_info()
    print(f"✅ Cache: {info['total_files']} plików, {info['total_size_mb']} MB")
    
    return True


def main():
    """Główna funkcja testowa."""
    print("=" * 70)
    print("🧪 FOREBET SCRAPER - TEST PODSTAWOWYCH FUNKCJONALNOŚCI")
    print("=" * 70)
    
    all_passed = True
    
    # Test importów
    if not test_imports():
        all_passed = False
    
    # Test konfiguracji
    try:
        if not test_config():
            all_passed = False
    except Exception as e:
        print(f"❌ Test konfiguracji nieudany: {e}")
        all_passed = False
    
    # Test sekretów
    try:
        if not test_secrets():
            all_passed = False
    except Exception as e:
        print(f"❌ Test sekretów nieudany: {e}")
        all_passed = False
    
    # Test loggera
    try:
        if not test_logger():
            all_passed = False
    except Exception as e:
        print(f"❌ Test loggera nieudany: {e}")
        all_passed = False
    
    # Test cache
    try:
        if not test_cache():
            all_passed = False
    except Exception as e:
        print(f"❌ Test cache nieudany: {e}")
        all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE!")
        print("=" * 70)
        print("\n🎯 Projekt jest gotowy do uruchomienia!")
        print("💡 Uruchom główny scraper: python main.py")
        return 0
    else:
        print("❌ NIEKTÓRE TESTY NIE PRZESZŁY")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

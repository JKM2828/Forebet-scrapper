"""
Automatyczna instalacja ChromeDriver dla Selenium.
"""
import sys

print("=" * 70)
print("🔧 INSTALACJA CHROMEDRIVER")
print("=" * 70)

try:
    print("\n📦 Instalowanie webdriver-manager...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
    print("✅ webdriver-manager zainstalowany!")
    
    print("\n🧪 Testowanie ChromeDriver...")
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("Pobieranie ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    
    print("Uruchamianie przeglądarki...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.google.com")
    print(f"✅ Tytuł strony: {driver.title}")
    driver.quit()
    
    print("\n" + "=" * 70)
    print("✅ CHROMEDRIVER DZIAŁA POPRAWNIE!")
    print("=" * 70)
    print("\n💡 Możesz teraz uruchomić: python main.py")
    
except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    print("\n📝 Alternatywne rozwiązanie:")
    print("1. Pobierz Chrome: https://www.google.com/chrome/")
    print("2. Pobierz ChromeDriver: https://chromedriver.chromium.org/downloads")
    print("3. Rozpakuj do C:\\chromedriver\\")
    print("4. Dodaj do PATH")
    sys.exit(1)

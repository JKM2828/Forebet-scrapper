"""
Minimalny test Gmail SMTP - szybkie sprawdzenie połączenia.
"""
import smtplib
import os
from pathlib import Path
from dotenv import load_dotenv

# Wczytaj .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_PASSWORD")

print(f"Gmail User: {gmail_user}")
print(f"Gmail Password: {'*' * 10 if gmail_password else 'BRAK'}")
print()

if not gmail_user or not gmail_password:
    print("BŁĄD: Brak konfiguracji!")
    exit(1)

try:
    print("Łączę z Gmail SMTP...")
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
    print("✓ Połączono")
    
    print("Loguję się...")
    server.login(gmail_user, gmail_password)
    print("✓ Zalogowano")
    
    server.quit()
    print("\n✅ SUKCES - Gmail SMTP działa poprawnie!")
    
except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    exit(1)

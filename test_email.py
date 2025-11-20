"""
Test wysyłania emaila - sprawdzenie konfiguracji Gmail SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config.secrets_manager import SecretsManager

def test_email():
    """Test wysyłania emaila."""
    secrets = SecretsManager()
    
    # Sprawdź konfigurację
    print("📧 Test konfiguracji Gmail SMTP")
    print(f"   Gmail User: {secrets.gmail_user}")
    print(f"   Gmail Password: {'*' * len(secrets.gmail_password) if secrets.gmail_password else 'BRAK'}")
    print(f"   Recipient: {secrets.recipient_email}")
    print()
    
    if not secrets.gmail_user or not secrets.gmail_password:
        print("❌ Brak konfiguracji Gmail!")
        return False
    
    # Tworzenie testowej wiadomości
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '🧪 Forebet Scraper - Test Email'
    msg['From'] = secrets.gmail_user
    msg['To'] = secrets.recipient_email
    
    html_content = """
    <html>
    <head></head>
    <body>
        <h2>✅ Test zakończony pomyślnie!</h2>
        <p>Forebet Scraper działa poprawnie.</p>
        <p>Konfiguracja Gmail SMTP jest prawidłowa.</p>
        <hr>
        <p><small>Wiadomość wygenerowana automatycznie przez test_email.py</small></p>
    </body>
    </html>
    """
    
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # Wysyłanie
    try:
        print("📤 Wysyłanie testowego emaila...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(secrets.gmail_user, secrets.gmail_password)
            server.send_message(msg)
        
        print(f"✅ Email wysłany pomyślnie do: {secrets.recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Błąd wysyłania: {e}")
        return False

if __name__ == "__main__":
    success = test_email()
    exit(0 if success else 1)

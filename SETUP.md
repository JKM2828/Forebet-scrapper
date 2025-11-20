# 📋 INSTRUKCJA SETUP - Forebet Scraper

## 🚀 Szybki Start

### 1. Klonowanie i Setup Lokalny

```bash
# Przejdź do folderu projektu
cd "c:\Users\jakub\Desktop\Forebet scrapper"

# Utwórz wirtualne środowisko
python -m venv venv

# Aktywuj środowisko (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Zainstaluj zależności
pip install -r requirements.txt

# Skopiuj przykładowy plik konfiguracyjny
copy .env.example .env

# Edytuj .env i uzupełnij dane (Gmail, etc.)
notepad .env
```

### 2. Konfiguracja Gmail App Password

⚠️ **WAŻNE:** NIE używaj zwykłego hasła Gmail!

1. Wejdź na: https://myaccount.google.com
2. Security → 2-Step Verification (włącz jeśli nie masz)
3. Security → App passwords
4. Generate new app password:
   - App: Mail
   - Device: Windows Computer
5. Skopiuj 16-znakowe hasło (format: `xxxx xxxx xxxx xxxx`)
6. Wklej do `.env` jako `GMAIL_PASSWORD` (bez spacji!)

### 3. Testowe Uruchomienie

```bash
# Uruchom scraper lokalnie
python main.py
```

### 4. Setup GitHub Repository

```bash
# Inicjalizuj Git (jeśli nie zrobione)
git init

# Dodaj pliki
git add .

# Commit
git commit -m "Initial commit - Forebet Scraper"

# Dodaj remote (zastąp YOUR_USERNAME swoim nickiem)
git remote add origin https://github.com/YOUR_USERNAME/forebet-scrapper.git

# Push do GitHub
git branch -M main
git push -u origin main
```

### 5. Konfiguracja GitHub Secrets

1. Wejdź na: `https://github.com/YOUR_USERNAME/forebet-scrapper/settings/secrets/actions`

2. Dodaj następujące sekrety (New repository secret):

   - **GMAIL_USER**
     - Value: `jakub.majka.zg@gmail.com`
   
   - **GMAIL_PASSWORD**
     - Value: Twój 16-znakowy App Password (bez spacji!)
   
   - **RECIPIENT_EMAIL**
     - Value: `jakub.majka.zg@gmail.com` (lub inny email odbiorcy)

### 6. Testowanie GitHub Actions

1. Wejdź na: Actions → Forebet Scraper Daily Run
2. Kliknij "Run workflow" → "Run workflow" (manual trigger)
3. Sprawdź logi wykonania
4. Sprawdź czy email dotarł

### 7. Harmonogram Automatyczny

GitHub Actions uruchomi scraper automatycznie o **2:00 UTC** każdego dnia.

Aby zmienić godzinę, edytuj `.github/workflows/forebet_scraper.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Format: minute hour day month weekday
```

Przykłady:
- `0 2 * * *` = 2:00 UTC każdego dnia
- `0 14 * * *` = 14:00 UTC każdego dnia
- `0 6 * * 1-5` = 6:00 UTC od poniedziałku do piątku

## 🔧 Troubleshooting

### Problem: ImportError - brak modułów

```bash
# Upewnij się, że środowisko jest aktywowane
.\venv\Scripts\Activate.ps1

# Reinstaluj zależności
pip install -r requirements.txt
```

### Problem: ChromeDriver nie działa

```bash
# Zainstaluj Chrome lub Chromium
# Windows: Pobierz Chrome z google.com/chrome
# Linux (GitHub Actions): Automatycznie instalowane w workflow
```

### Problem: Email się nie wysyła

- Sprawdź czy używasz **App Password**, nie zwykłego hasła
- Sprawdź czy 2-Step Verification jest włączona w Gmail
- Sprawdź logi: `logs/forebet_scraper.log`
- Test połączenia SMTP:
  ```python
  python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); print('OK')"
  ```

### Problem: GitHub Actions fail

- Sprawdź czy wszystkie 3 sekrety są ustawione
- Sprawdź logi w zakładce Actions
- Sprawdź czy repo jest publiczne/private (private wymaga płatnego planu)

## 📊 Monitorowanie

### Logi lokalne
```bash
# Zobacz ostatnie logi
Get-Content logs/forebet_scraper.log -Tail 50

# Zobacz tylko błędy
Get-Content logs/forebet_scraper_errors.log
```

### Logi GitHub Actions
1. Wejdź na: Actions → Wybierz run
2. Kliknij na "scrape-and-notify"
3. Zobacz szczegółowe logi każdego kroku

### Cache Info
```python
python -c "from src.data_management import cache_manager; print(cache_manager.get_cache_info())"
```

## 🧪 Testy

```bash
# Uruchom wszystkie testy
pytest tests/

# Z coverage
pytest --cov=src tests/

# Konkretny test
pytest tests/test_scraper.py -v
```

## 📝 Development

```bash
# Code formatting
pip install black flake8 isort mypy

# Format code
black src/ tests/ main.py

# Linting
flake8 src/

# Type checking
mypy src/

# Sort imports
isort src/ tests/ main.py
```

## 🎯 Dalsze Kroki

1. **Testuj lokalnie** przed pushem do GitHub
2. **Monitoruj logi** przez pierwszy tydzień
3. **Dostosuj** progi i kryteria w `.env`
4. **Rozbuduj** parsery jeśli struktura Forebet się zmieni
5. **Dodaj** więcej źródeł kursów (LiveSport, itp.)

## 📧 Wsparcie

- Email: jakub.majka.zg@gmail.com
- Logi: `logs/forebet_scraper.log`
- Issues: GitHub Issues tab

---

**Powodzenia! ⚽🎯**

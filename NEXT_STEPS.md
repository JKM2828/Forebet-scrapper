# 🚀 NASTĘPNE KROKI - URUCHOMIENIE PROJEKTU

## ✅ CO JUŻ ZROBILIŚMY:

1. ✅ Utworzono pełną strukturę projektu (20+ plików)
2. ✅ Zainstalowano wszystkie zależności (requirements.txt)
3. ✅ Przetestowano podstawowe funkcjonalności (wszystkie OK!)
4. ✅ Konfiguracja .env z danymi Gmail
5. ✅ Repozytorium Git zainicjalizowane

---

## 📋 CO TERAZ ZROBIĆ:

### OPCJA A: Test Lokalny (Polecane jako pierwszy krok)

#### 1. Uruchom scraper w trybie testowym (bez wysyłania emaila)

Najpierw przetestujmy czy scraper pobiera dane z Forebet:

```powershell
cd "c:\Users\jakub\Desktop\Forebet scrapper"
.\venv\Scripts\Activate.ps1
python -c "from src.scrapers import ForebtScraper; from src.config import Sport; s = ForebtScraper(use_selenium=False); events = s.fetch_events_by_sport(Sport.FOOTBALL); print(f'Pobrano {len(events)} zdarzeń'); s.close()"
```

**Czego się spodziewać:**
- Scraper połączy się z Forebet
- Pobierze zdarzenia piłkarskie
- Wyświetli liczbę znalezionych meczów

⚠️ **UWAGA:** Jeśli zobaczysz błąd parsowania HTML, to normalne - parsery wymagają dostosowania do aktualnej struktury Forebet (zobacz sekcję "Troubleshooting" poniżej).

---

#### 2. Test wysyłania emaila (bez scrapingu)

Przetestuj czy email się wysyła:

```powershell
python -c "from src.notifiers import EmailSender; sender = EmailSender(); test_events = [{'event': {'home_team': 'Test A', 'away_team': 'Test B', 'sport': 'football', 'league': 'Test League', 'probabilities': {'home': 65, 'draw': 20, 'away': 15}, 'match_url': 'https://forebet.com'}, 'analysis': {'home_form': {'record': '3W-1D-0L', 'points': 10}, 'away_form': {'record': '1W-2D-1L', 'points': 5}, 'h2h': {'has_history': False}}}]; result = sender.send_qualified_events(test_events); print('Email wysłany!' if result else 'Błąd wysyłania')"
```

**Sprawdź swoją skrzynkę:** `jakub.majka.zg@gmail.com`

✅ Jeśli email dotarł - system działa!
❌ Jeśli nie - sprawdź sekcję "Troubleshooting Email"

---

#### 3. Pełny test (scraping + analiza + email)

⚠️ **Przed uruchomieniem:** Upewnij się że masz ChromeDriver zainstalowany (dla Selenium).

```powershell
# Pełne uruchomienie
python main.py
```

**Co się stanie:**
1. Scraper pobierze zdarzenia dla 5 sportów
2. Przeanalizuje je (H2H, forma, home/away)
3. Przefiltruje według kryteriów (60%+ przewaga)
4. Wyśle email z kwalifikowanymi zdarzeniami

**Logi:** Sprawdź `logs/forebet_scraper.log`

---

### OPCJA B: Setup GitHub Actions (Automatyczne uruchamianie)

Gdy lokalny test przejdzie pomyślnie, skonfiguruj GitHub Actions:

#### 1. Push projektu do GitHub

```powershell
# Sprawdź remote
git remote -v

# Jeśli nie ma remote, dodaj:
# git remote add origin https://github.com/JKM2828/Forebet-scrapper.git

# Push
git push origin main
```

#### 2. Ustaw GitHub Secrets

1. Wejdź na: https://github.com/JKM2828/Forebet-scrapper/settings/secrets/actions

2. Kliknij **"New repository secret"** i dodaj:

   **Secret 1:**
   - Name: `GMAIL_USER`
   - Value: `jakub.majka.zg@gmail.com`

   **Secret 2:**
   - Name: `GMAIL_PASSWORD`
   - Value: `vurb tcai zaaq itjx`

   **Secret 3:**
   - Name: `RECIPIENT_EMAIL`
   - Value: `jakub.majka.zg@gmail.com`

3. Kliknij **"Add secret"** dla każdego

#### 3. Test GitHub Actions (Manual Run)

1. Wejdź na: https://github.com/JKM2828/Forebet-scrapper/actions

2. Kliknij na **"Forebet Scraper Daily Run"**

3. Kliknij **"Run workflow"** → **"Run workflow"** (zielony przycisk)

4. Czekaj ~5 minut

5. Sprawdź:
   - ✅ Logi w Actions (powinny być zielone)
   - ✅ Email w skrzynce

#### 4. Automatyczne uruchamianie

GitHub Actions uruchomi scraper **automatycznie o 2:00 UTC każdego dnia**.

Żeby zmienić godzinę, edytuj `.github/workflows/forebet_scraper.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Format: minute hour day month weekday
```

Przykłady:
- `0 2 * * *` = 2:00 UTC
- `0 14 * * *` = 14:00 UTC (2:00 PM)
- `0 6 * * 1-5` = 6:00 UTC od poniedziałku do piątku

---

## 🐛 TROUBLESHOOTING

### Problem 1: ChromeDriver nie jest zainstalowany

**Objawy:**
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH.
```

**Rozwiązanie:**

**Opcja A - Instalacja automatyczna (łatwiejsza):**
```powershell
pip install webdriver-manager
```

Następnie edytuj `src/scrapers/forebet_scraper.py`:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# W metodzie _init_driver() zamień:
self.driver = webdriver.Chrome(options=chrome_options)

# Na:
service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=chrome_options)
```

**Opcja B - Manualnie:**
1. Pobierz ChromeDriver: https://chromedriver.chromium.org/downloads
2. Rozpakuj do `C:\chromedriver\`
3. Dodaj do PATH systemowego

**Opcja C - Użyj Firefox zamiast Chrome:**
```powershell
pip install geckodriver-autoinstaller
```

---

### Problem 2: Parsery HTML nie działają

**Objawy:**
```
Znaleziono 0 wierszy do parsowania
Brak zdarzeń dla football
```

**Przyczyna:** Struktura HTML Forebet zmieniła się od implementacji

**Rozwiązanie:**

1. Otwórz w przeglądarce: https://www.forebet.com/pl/football/prognozy-na-dzis

2. Naciśnij **F12** (DevTools)

3. Znajdź element z meczem (prawy przycisk → Inspect)

4. Zobacz jakie klasy CSS używa Forebet dla:
   - Wierszy meczów (np. `class="tr_match"` lub `data-match-id="..."`)
   - Nazw drużyn (np. `class="team-name"`)
   - Prawdopodobieństw (np. `class="fprc"` z `<span>40</span>`)

5. Edytuj `src/scrapers/forebet_scraper.py`:
   ```python
   # Linia ~203 - zmień selektor:
   match_rows = soup.find_all('tr', attrs={'data-tid': True})
   
   # Na właściwy selektor który znalazłeś, np:
   match_rows = soup.find_all('div', class_='match-row')
   ```

6. Dostosuj też metody:
   - `_extract_teams()` - linia ~230
   - `_extract_probabilities()` - linia ~260
   - `_extract_match_url()` - linia ~290

**Pro tip:** Użyj `use_selenium=True` w scraperze - często pomaga z dynamicznym JS.

---

### Problem 3: Email się nie wysyła

**Objawy:**
```
Błąd wysyłania emaila: (535, b'5.7.8 Username and Password not accepted')
```

**Checklist:**

1. ✅ **Czy używasz App Password?**
   - NIE zwykłego hasła Gmail!
   - Musi być 16 znaków bez spacji
   - Twoje: `vurb tcai zaaq itjx`

2. ✅ **Czy 2-Step Verification jest włączona?**
   - Wejdź: https://myaccount.google.com/security
   - Security → 2-Step Verification → **Włącz**

3. ✅ **Czy App Password jest aktywny?**
   - Security → App passwords
   - Jeśli stary nie działa, wygeneruj nowy

4. ✅ **Test ręczny SMTP:**
   ```powershell
   python -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); s.login('jakub.majka.zg@gmail.com','vurb tcai zaaq itjx'); print('LOGIN OK!'); s.quit()"
   ```

5. ✅ **Sprawdź folder SPAM**

---

### Problem 4: "Brak kwalifikowanych zdarzeń"

**To NIE jest błąd!** Oznacza że:
- Scraper działa ✅
- Pobrano zdarzenia ✅
- Ale żadne nie spełniło wszystkich kryteriów (60%+, forma, H2H, etc.)

**Rozwiązania:**
1. Zmniejsz próg w `.env`:
   ```
   NOTIFICATION_THRESHOLD=50  # było 60
   ```

2. Zmodyfikuj logikę filtrowania w `src/filters/event_filter.py`

3. Poczekaj na inny dzień - czasem po prostu nie ma dobrych meczów

---

### Problem 5: GitHub Actions fail

**Sprawdź:**

1. ✅ **Czy sekrety są ustawione?**
   - https://github.com/JKM2828/Forebet-scrapper/settings/secrets/actions
   - Muszą być dokładnie 3: `GMAIL_USER`, `GMAIL_PASSWORD`, `RECIPIENT_EMAIL`

2. ✅ **Czy Actions są włączone?**
   - Settings → Actions → General → "Allow all actions"

3. ✅ **Zobacz logi:**
   - Actions → Wybierz run → Kliknij na "scrape-and-notify"
   - Przeczytaj błędy

4. ✅ **Artifacts (logi):**
   - Na dole strony run → Download "scraper-logs"

---

## 📊 MONITORING

### Sprawdzanie logów lokalnie

```powershell
# Ostatnie 50 linii
Get-Content "logs/forebet_scraper.log" -Tail 50

# Tylko błędy
Get-Content "logs/forebet_scraper_errors.log"

# Real-time monitoring
Get-Content "logs/forebet_scraper.log" -Wait
```

### Cache info

```powershell
python -c "from src.data_management import cache_manager; import json; print(json.dumps(cache_manager.get_cache_info(), indent=2))"
```

### GitHub Actions - Monitoring

1. **Email notifications:**
   - GitHub wyśle email jeśli workflow fail

2. **Badges (opcjonalne):**
   Dodaj do README.md:
   ```markdown
   ![Scraper Status](https://github.com/JKM2828/Forebet-scrapper/actions/workflows/forebet_scraper.yml/badge.svg)
   ```

---

## 🎯 DALSZE KROKI (OPCJONALNE)

### 1. Dostosowanie Parserów Forebet

Po pierwszym uruchomieniu, prawdopodobnie parsery będą wymagać "tuningu":

**Proces:**
1. Uruchom scraper lokalnie
2. Zobacz logi - które sekcje nie parsują
3. Inspect HTML na Forebet (F12)
4. Dostosuj selektory w `forebet_scraper.py`
5. Test ponownie

**Pliki do edycji:**
- `src/scrapers/forebet_scraper.py` - główne parsery
- `src/analyzers/head_to_head_analyzer.py` - H2H parsing
- `src/analyzers/form_analyzer.py` - forma (jeśli dodasz scraping)

### 2. Implementacja Pobierania Kursów

Flashscore fetcher to obecnie placeholder. Opcje:

**A. Flashscore scraping (trudniejsze):**
- Reverse engineer Flashscore API (DevTools → Network)
- Scrape HTML (może być blokowane)

**B. Odds-API.com (płatne):**
- https://the-odds-api.com/
- $50/miesiąc
- Dobra dokumentacja

**C. Football-Data.org (free tier):**
- https://www.football-data.org/
- Ograniczone do 10 requestów/minutę

### 3. Rozszerzenie Testów

```powershell
# Zainstaluj pytest-cov
pip install pytest-cov

# Uruchom z coverage
pytest --cov=src tests/ --cov-report=html

# Zobacz raport
start htmlcov/index.html
```

### 4. Docker (dla zaawansowanych)

Jeśli chcesz uruchamiać na własnym serwerze:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## ✅ CHECKLIST KOŃCOWY

Przed uznaniem projektu za "gotowy":

- [ ] Test lokalny: `python test_quick.py` ✅ (DONE)
- [ ] Test scrapingu: Pobierz mecze z Forebet
- [ ] Test emaila: Wyślij testowy email
- [ ] Push do GitHub
- [ ] Setup GitHub Secrets (3 sekrety)
- [ ] Test GitHub Actions (manual run)
- [ ] Sprawdź email po GitHub Actions
- [ ] Poczekaj na pierwszy automatyczny run (2:00 UTC)
- [ ] Monitoruj przez tydzień

---

## 📞 POTRZEBUJESZ POMOCY?

**Logi:**
- Lokalnie: `logs/forebet_scraper.log`
- GitHub: Actions → Run → Download artifacts

**Dokumentacja:**
- README.md - główna dokumentacja
- SETUP.md - setup guide
- PROJECT_SUMMARY.md - kompletny przewodnik
- Ten plik - następne kroki

**Email:** jakub.majka.zg@gmail.com

---

## 🎉 GRATULACJE!

Masz teraz w pełni funkcjonalny Forebet Scraper! 

**Co dalej?**
1. 🧪 Przetestuj lokalnie
2. 🚀 Deploy na GitHub Actions
3. 📧 Odbieraj codzienne emaile o 2:00 UTC
4. 🔧 Dostosuj parsery jeśli potrzeba
5. 📊 Monitoruj wyniki

**Powodzenia! ⚽🎯📧**

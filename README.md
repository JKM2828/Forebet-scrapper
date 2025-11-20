# Forebet Scraper 🎯⚽

Automatyczny system monitorowania zdarzeń sportowych na platformie Forebet z filtrowaniem według przewagi matematycznej (60%+) i wysyłaniem powiadomień email.

## 📋 Funkcjonalności

- ✅ Scraping zdarzeń sportowych z Forebet (piłka nożna, koszykówka, siatkówka, hokej, itp.)
- ✅ Filtrowanie po przewadze matematycznej 60%+
- ✅ Analiza historii meczów H2H (head-to-head)
- ✅ Analiza formy drużyn (ostatnie mecze)
- ✅ Statystyki u siebie/na wyjeździe
- ✅ Pobieranie kursów z różnych źródeł (Flashscore, LiveSport)
- ✅ Wysyłanie powiadomień email z kwalifikowanymi zdarzeniami
- ✅ Automatyczne uruchamianie o 2:00 via GitHub Actions

## 🚀 Szybki Start

### 1. Instalacja

```bash
# Klonuj repozytorium
git clone https://github.com/your-username/forebet-scrapper.git
cd forebet-scrapper

# Utwórz virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Zainstaluj zależności
pip install -r requirements.txt
```

### 2. Konfiguracja

Skopiuj `.env.example` do `.env` i uzupełnij dane:

```bash
cp .env.example .env
```

**Wymagane zmienne:**
- `GMAIL_USER` - Twój email Gmail
- `GMAIL_PASSWORD` - **App Password** (nie zwykłe hasło!)
- `RECIPIENT_EMAIL` - Email odbiorcy powiadomień

### 3. Google App Password

⚠️ **WAŻNE:** Musisz użyć App Password, nie zwykłego hasła Gmail!

1. Wejdź na https://myaccount.google.com
2. Security → 2-Step Verification (włącz jeśli nie masz)
3. App passwords → Mail → Generate
4. Skopiuj 16-znakowe hasło do `.env` jako `GMAIL_PASSWORD`

### 4. Uruchomienie

```bash
# Uruchom lokalnie
python main.py
```

## 🏗️ Struktura Projektu

```
forebet-scrapper/
├── src/
│   ├── scrapers/          # Web scraping Forebet
│   ├── analyzers/         # Analiza H2H, formy, home/away
│   ├── odds_fetchers/     # Pobieranie kursów
│   ├── filters/           # Logika filtrowania zdarzeń
│   ├── notifiers/         # Wysyłanie emaili
│   ├── data_management/   # Cache, logging
│   ├── config/            # Konfiguracja i secrets
│   └── utils/             # Narzędzia pomocnicze
├── tests/                 # Testy jednostkowe
├── logs/                  # Logi aplikacji
├── cache/                 # Cache danych
├── .github/workflows/     # GitHub Actions
├── main.py                # Entry point
├── requirements.txt       # Zależności
└── .env.example           # Przykładowa konfiguracja
```

## 🔄 GitHub Actions - Automatyczne Uruchamianie

Projekt uruchamia się automatycznie o 2:00 UTC każdego dnia.

### Setup GitHub Secrets:

1. Wejdź: `Settings → Secrets and variables → Actions`
2. Dodaj sekrety:
   - `GMAIL_USER` = twój email
   - `GMAIL_PASSWORD` = App Password
   - `RECIPIENT_EMAIL` = email odbiorcy

## 🎯 Algorytm Kwalifikacji Zdarzenia

Zdarzenie jest kwalifikowane gdy spełnia **wszystkie** warunki:

1. **Przewaga matematyczna** ≥ 60%
2. **Historia H2H** (jeśli dostępna):
   - Drużyna ma ≥60% wygranych w meczach bezpośrednich
   - Jeśli brak historii → przejdź do kroku 3
3. **Forma ogólna**:
   - Wskazana drużyna ma lepszą formę (więcej punktów z ostatnich meczów)
4. **Home/Away**:
   - Gospodarz ma lepszą formę u siebie
   - Gość ma słabszą formę na wyjeździe
5. **Kursy**:
   - Dostępne kursy z co najmniej 1 źródła

## 📧 Format Emaila

Email zawiera:
- Datę i godzinę generacji
- Liczbę kwalifikowanych zdarzeń
- Tabelę z detalami każdego zdarzenia:
  - Drużyny
  - Sport i liga
  - Przewaga matematyczna (%)
  - Forma drużyn
  - Statystyki H2H
  - Dostępne kursy
  - Link do Forebet

## 🧪 Testy

```bash
# Uruchom wszystkie testy
pytest tests/

# Z coverage
pytest --cov=src tests/

# Konkretny test
pytest tests/test_scraper.py
```

## 🛠️ Development

```bash
# Formatowanie kodu
black src/

# Linting
flake8 src/

# Type checking
mypy src/

# Import sorting
isort src/
```

## ⚠️ Troubleshooting

### Problem: Email nie wysyła się
- Sprawdź czy używasz **App Password**, nie zwykłego hasła
- Sprawdź czy 2-Step Verification jest włączona w Gmail
- Sprawdź logi: `logs/forebet_scraper.log`

### Problem: Scraper nie pobiera danych
- Forebet może zmienić strukturę HTML
- Sprawdź rate limiting (dodaj `time.sleep()`)
- Sprawdź User-Agent headers

### Problem: GitHub Actions nie działa
- Sprawdź czy sekrety są ustawione w repozytorium
- Sprawdź timezone (cron używa UTC)
- Zobacz logi w zakładce Actions

## 📝 TODO / Roadmap

- [ ] Multi-sport expansion (wszystkie 9 sportów)
- [ ] Database persistence (SQLite)
- [ ] Analytics dashboard
- [ ] Telegram/Slack notifications
- [ ] Machine learning model dla quality picks
- [ ] Docker containerization

## 📄 Licencja

MIT License

## 🤝 Contributing

Pull requesty są mile widziane! Dla dużych zmian, najpierw otwórz issue.

## 📞 Kontakt

Email: jakub.majka.zg@gmail.com

---

**Uwaga:** Projekt jest do celów edukacyjnych. Respektuj Terms of Service stron, z których scrapujesz dane.

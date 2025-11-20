# ⚙️ GITHUB ACTIONS - SETUP GUIDE

## Automatyczne Uruchamianie Forebet Scraper

### 📅 Harmonogram:
System jest skonfigurowany do automatycznego uruchamiania **codziennie o 2:00 UTC** (3:00 CET w zimie, 4:00 CEST w lecie).

---

## 🔐 KROK 1: Dodaj Sekrety do GitHub

### Gdzie?
https://github.com/JKM2828/Forebet-scrapper/settings/secrets/actions

### Jakie sekrety?

Dodaj następujące 3 sekrety:

#### 1. `GMAIL_USER`
```
Nazwa: GMAIL_USER
Wartość: jakub.majka.zg@gmail.com
```

#### 2. `GMAIL_PASSWORD`
```
Nazwa: GMAIL_PASSWORD
Wartość: vurb tcai zaaq itjx
```
⚠️ **WAŻNE**: To jest **App Password**, NIE zwykłe hasło Gmail!

#### 3. `RECIPIENT_EMAIL`
```
Nazwa: RECIPIENT_EMAIL
Wartość: jakub.majka.zg@gmail.com
```
(lub inny email, jeśli chcesz otrzymywać powiadomienia gdzie indziej)

---

## 🚀 KROK 2: Uruchom Ręcznie (Test)

### Jak przetestować workflow?

1. Idź do: https://github.com/JKM2828/Forebet-scrapper/actions

2. Wybierz: **"Forebet Scraper Daily Run"** z listy workflows

3. Kliknij: **"Run workflow"** (przycisk po prawej)

4. Wybierz branch: `main` (lub `master`)

5. Kliknij: **"Run workflow"** (zielony przycisk)

6. Poczekaj 2-5 minut

7. Sprawdź rezultat:
   - ✅ Zielony check = sukces
   - ❌ Czerwony X = błąd

### Co się dzieje podczas workflow?

```
1. Checkout repository
   └─> Pobiera kod z GitHub

2. Setup Python 3.11
   └─> Instaluje Python i cache pip

3. Install dependencies
   └─> pip install -r requirements.txt

4. Install Chrome + ChromeDriver
   └─> Instaluje przeglądarkę (Ubuntu)

5. Run Forebet Scraper
   └─> python main.py
   └─> Używa sekretów z GitHub Secrets
   └─> Wysyła email jeśli znajdzie kwalifikujące się wydarzenia

6. Upload logs (jeśli błąd)
   └─> Zapisuje logi jako artifacts do debugowania
```

---

## 📊 KROK 3: Sprawdź Logi

### Jak zobaczyć co się działo?

1. Idź do: https://github.com/JKM2828/Forebet-scrapper/actions

2. Kliknij na konkretne uruchomienie workflow

3. Kliknij na "scrape-and-notify" (job name)

4. Zobaczysz szczegółowe logi każdego kroku

### Jeśli wystąpił błąd:

- Sprawdź sekcję "Run Forebet Scraper"
- Pobierz artifacts (logs/) jeśli zostały zapisane
- Sprawdź czy sekrety są poprawnie ustawione

---

## 🔄 KROK 4: Zrozum Harmonogram (Cron)

### Cron Expression:
```yaml
cron: '0 2 * * *'
```

**Co to znaczy:**
- `0` = minuta 0
- `2` = godzina 2 (UTC)
- `*` = każdy dzień miesiąca
- `*` = każdy miesiąc
- `*` = każdy dzień tygodnia

**W praktyce:** 
- Workflow uruchamia się **codziennie o 2:00 UTC**
- W Polsce: 3:00 (czas zimowy) lub 4:00 (czas letni)

### Jak zmienić harmonogram?

Edytuj `.github/workflows/forebet_scraper.yml`:
```yaml
on:
  schedule:
    # Przykłady:
    - cron: '0 6 * * *'     # Codziennie o 6:00 UTC
    - cron: '0 8,20 * * *'  # Codziennie o 8:00 i 20:00 UTC
    - cron: '0 2 * * 1-5'   # Poniedziałek-Piątek o 2:00 UTC
```

**Narzędzie do generowania:** https://crontab.guru/

---

## 📧 Co otrzymasz?

### Jeśli znajdą się kwalifikujące wydarzenia (60%+):
- Dostaniesz email z:
  - Listą meczów
  - Szczegółami każdego meczu
  - Statystykami H2H
  - Formą drużyn
  - Kursami bukmacherskimi

### Jeśli nie znajdą się wydarzenia:
- Nie dostaniesz emaila
- Workflow zakończy się sukcesem (✅)
- Logi będą zawierać informację: "Brak kwalifikowanych zdarzeń"

---

## 🐛 Troubleshooting

### Problem 1: Workflow Failed (❌)
**Możliwe przyczyny:**
- Sekrety niepoprawnie skonfigurowane
- Forebet.com zablokował dostęp (rate limiting)
- Błąd w parsowaniu HTML (Forebet zmienił strukturę)

**Rozwiązanie:**
1. Sprawdź logi workflow
2. Pobierz artifacts (jeśli są)
3. Uruchom lokalnie: `python main.py` aby zdiagnozować
4. Sprawdź czy sekrety są poprawne

### Problem 2: Nie otrzymujesz emaili
**Możliwe przyczyny:**
- Brak kwalifikujących się zdarzeń (60%+ threshold)
- Sekrety Gmail niepoprawne
- Gmail blokuje logowanie

**Rozwiązanie:**
1. Sprawdź logi workflow - czy znalazł jakieś wydarzenia?
2. Uruchom lokalnie: `python test_email.py`
3. Sprawdź czy `GMAIL_PASSWORD` to **App Password**
4. Sprawdź spam folder

### Problem 3: Workflow nie uruchamia się automatycznie
**Możliwe przyczyny:**
- GitHub Actions są wyłączone
- Repository jest private i brak minut Actions
- Cron schedule niepoprawny

**Rozwiązanie:**
1. Sprawdź: https://github.com/JKM2828/Forebet-scrapper/settings/actions
2. Upewnij się że Actions są włączone
3. Sprawdź usage: https://github.com/settings/billing

---

## 💡 Wskazówki

### Testowanie przed deployment:
```powershell
# Lokalnie (Windows):
python main.py

# Lokalnie z tymi samymi zmiennymi co GitHub:
$env:HEADLESS_BROWSER="true"
$env:NOTIFICATION_THRESHOLD="60"
python main.py
```

### Monitorowanie:
- Sprawdzaj: https://github.com/JKM2828/Forebet-scrapper/actions co jakiś czas
- Email jest wysyłany tylko jeśli są kwalifikujące się wydarzenia
- Logi są zawsze dostępne w Actions (nawet jeśli nie ma błędów)

### Optymalizacja:
```yaml
# W .github/workflows/forebet_scraper.yml

# Zmniejsz liczbę sportów (przyspieszy workflow):
env:
  SPORTS_TO_ANALYZE: football,basketball  # Zamiast wszystkich 5

# Zmień próg (więcej/mniej emaili):
env:
  NOTIFICATION_THRESHOLD: 55  # Łatwiejszy próg = więcej emaili
```

---

## ✅ Checklist Setup

- [ ] Dodałem `GMAIL_USER` do GitHub Secrets
- [ ] Dodałem `GMAIL_PASSWORD` do GitHub Secrets (App Password!)
- [ ] Dodałem `RECIPIENT_EMAIL` do GitHub Secrets
- [ ] Uruchomiłem workflow ręcznie (test)
- [ ] Sprawdziłem logi workflow
- [ ] Otrzymałem testowy email (jeśli były wydarzenia)
- [ ] Sprawdzam Actions co kilka dni aby upewnić się że działa

---

## 🎯 Podsumowanie

Po zakończeniu setup:
- ✅ System uruchamia się automatycznie codziennie o 2:00 UTC
- ✅ Wysyła emaile tylko gdy znajdzie interesujące mecze (60%+)
- ✅ Możesz monitorować w GitHub Actions
- ✅ Możesz uruchamiać ręcznie w każdej chwili

**GitHub Actions jest w pełni skonfigurowany i gotowy do użycia!** 🚀

---

**Autor**: Copilot AI
**Data**: 2025-11-21
**Wersja**: 1.0.0

# 📊 Implementacja pobierania kursów z Flashscore/LiveSport

## ⚠️ Aktualny status

**WAŻNE:** `flashscore_fetcher.py` jest obecnie **PLACEHOLDEREM** i **NIE POBIERA** rzeczywistych kursów z Flashscore/LiveSport API.

### Dlaczego kursy nie działają?

```python
# src/odds_fetchers/flashscore_fetcher.py - AKTUALNY KOD
def fetch_odds(self, match_id: str, home_team: str, away_team: str) -> Dict[str, Any]:
    """
    PLACEHOLDER - implementacja wymaga reverse engineeringu Flashscore/LiveSport API
    """
    return {
        'has_odds': False,  # ❌ Zawsze False!
        'home_win': None,
        'draw': None,
        'away_win': None,
        'source': 'placeholder',
        'note': 'Placeholder - wymaga implementacji scraping Flashscore'
    }
```

### W emailu zobaczysz:
- Kursy **nie będą wyświetlane** (bo `has_odds: False`)
- Forma zespołów **TERAZ DZIAŁA** ✅ (po naprawie demo.py)

---

## 🔧 Jak zaimplementować pobieranie kursów?

### Metoda 1: Reverse engineering Flashscore API (ZAAWANSOWANE)

Flashscore/LiveSport używa wewnętrznego API które jest chronione. Wymaga:

1. **Analiza ruchu sieciowego:**
   ```bash
   # Otwórz Chrome DevTools → Network
   # Wejdź na https://www.flashscore.pl/
   # Filtruj XHR/Fetch requests
   # Szukaj endpoints z danymi meczów i kursów
   ```

2. **Znajdź endpoint API:**
   - Przykład: `https://d.flashscore.com/x/feed/...`
   - Sprawdź headers (User-Agent, Referer, cookies)
   - Sprawdź parametry query (?stage=, ?project=)

3. **Implementuj w `flashscore_fetcher.py`:**
   ```python
   def fetch_odds(self, match_id: str, home_team: str, away_team: str):
       headers = {
           'User-Agent': '...',
           'Referer': 'https://www.flashscore.pl/',
           'X-Fsign': '...'  # Token autoryzacji
       }
       
       response = requests.get(
           f'https://d.flashscore.com/x/feed/{match_id}',
           headers=headers
       )
       
       data = response.json()
       # Parsuj kursy z JSON
   ```

### Metoda 2: Web Scraping Flashscore (ŚREDNIE)

Użyj Selenium do scrapowania strony:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def fetch_odds(self, match_id: str, home_team: str, away_team: str):
    # Wyszukaj mecz po nazwach drużyn
    url = f"https://www.flashscore.pl/wyszukiwanie/?q={home_team} {away_team}"
    
    driver = webdriver.Chrome()
    driver.get(url)
    
    # Kliknij w mecz
    match_elem = driver.find_element(By.CSS_SELECTOR, ".event__match")
    match_elem.click()
    
    # Przejdź do zakładki "Kursy"
    odds_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Kursy')]")
    odds_tab.click()
    
    # Znajdź kursy 1X2
    home_odd = driver.find_element(By.CSS_SELECTOR, ".oddsCell__odd:nth-child(1)").text
    draw_odd = driver.find_element(By.CSS_SELECTOR, ".oddsCell__odd:nth-child(2)").text
    away_odd = driver.find_element(By.CSS_SELECTOR, ".oddsCell__odd:nth-child(3)").text
    
    driver.quit()
    
    return {
        'has_odds': True,
        'home_win': float(home_odd),
        'draw': float(draw_odd),
        'away_win': float(away_odd),
        'source': 'flashscore'
    }
```

### Metoda 3: Użyj API bukmacherskiego (ŁATWE ale PŁATNE)

Alternatywa: API zewnętrzne (np. Odds API, The Odds API):

```python
import requests

def fetch_odds_from_api(self, home_team: str, away_team: str):
    # https://the-odds-api.com/
    API_KEY = 'your_api_key'
    
    response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/soccer_poland_ekstraklasa/odds',
        params={
            'apiKey': API_KEY,
            'regions': 'eu',
            'markets': 'h2h',
            'oddsFormat': 'decimal'
        }
    )
    
    data = response.json()
    
    # Znajdź mecz po nazwach drużyn
    for event in data:
        if home_team in event['home_team'] and away_team in event['away_team']:
            bookmaker = event['bookmakers'][0]
            odds = bookmaker['markets'][0]['outcomes']
            
            return {
                'has_odds': True,
                'home_win': odds[0]['price'],
                'draw': odds[1]['price'] if len(odds) > 2 else None,
                'away_win': odds[-1]['price'],
                'source': bookmaker['title']
            }
```

---

## 🚀 Rekomendowane podejście

### Dla szybkiej implementacji:
1. **Użyj Metody 2 (Selenium scraping)**
   - Najłatwiejsze do zaimplementowania
   - Nie wymaga API keys
   - Działa od razu

### Dla produkcyjnego użytku:
1. **Metoda 1 (Reverse engineering API)**
   - Najszybsze (bez Selenium)
   - Bardziej stabilne
   - Wymaga analizy

### Dla gotowego rozwiązania:
1. **Metoda 3 (Zewnętrzne API)**
   - Płatne ($50-200/msc)
   - Gotowe dane
   - Wysoka jakość

---

## 📝 TODO: Implementacja kursów

```python
# src/odds_fetchers/flashscore_fetcher.py

class FlashscoreFetcher:
    def __init__(self):
        self.session = requests.Session()
        # LUB
        self.driver = webdriver.Chrome()
    
    def fetch_odds(self, match_id: str, home_team: str, away_team: str):
        """
        TODO: Zaimplementuj jedną z metod:
        1. Reverse engineering API
        2. Selenium scraping
        3. Zewnętrzne API
        """
        try:
            # TWOJA IMPLEMENTACJA TUTAJ
            
            return {
                'has_odds': True,
                'home_win': 1.85,
                'draw': 3.40,
                'away_win': 4.20,
                'source': 'flashscore'
            }
        except Exception as e:
            logger.error(f"Błąd pobierania kursów: {e}")
            return {
                'has_odds': False,
                'home_win': None,
                'draw': None,
                'away_win': None
            }
```

---

## ⚡ Natychmiastowe obejście

Jeśli chcesz **tymczasowo** przetestować system bez kursów:

```python
# main.py - zakomentuj pobieranie kursów
# odds = odds_aggregator.aggregate_odds(match_id, home_team, away_team)

# Użyj pustych kursów
odds = {'has_odds': False, 'home_win': None, 'draw': None, 'away_win': None}
```

**LUB** zmień `email_sender.py` aby nie wyświetlał sekcji z kursami gdy `has_odds == False`.

---

## 📚 Dodatkowe zasoby

- [Flashscore.pl](https://www.flashscore.pl/)
- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [Selenium Python Docs](https://selenium-python.readthedocs.io/)
- [Requests Library](https://requests.readthedocs.io/)

---

## ✅ Podsumowanie

| Co działa? | Status |
|------------|--------|
| Pobieranie wydarzeń z Forebet | ✅ DZIAŁA |
| Prawdopodobieństwa 1/X/2 | ✅ DZIAŁA |
| Forma ogólna zespołów | ✅ DZIAŁA (po naprawie) |
| Forma home/away | ✅ DZIAŁA (po naprawie) |
| Historia H2H | ✅ DZIAŁA |
| **Kursy z Flashscore** | ❌ **PLACEHOLDER - DO IMPLEMENTACJI** |
| Email z gradientem | ✅ DZIAŁA |
| Grupowanie po sportach | ✅ DZIAŁA |

---

**Priorytet:** Jeśli kursy są krytyczne dla Twojego use case, zalecam **Metodę 2 (Selenium scraping)** jako najszybsze rozwiązanie.

**Kontakt:** Daj znać jeśli potrzebujesz pomocy z implementacją którejś z metod!

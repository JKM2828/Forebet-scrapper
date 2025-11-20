# 🚀 QUICK START GUIDE

## Najszybszy sposób na uruchomienie Forebet Scraper

### ⚡ 3 Proste Kroki:

#### 1. **Uruchom Demo** (polecane na początek)
```powershell
python demo.py
```
**Co się stanie:**
- System przetworzy 3 symulowane mecze
- Pokaże pełny proces: scraping → analiza → filtrowanie → email
- **Wyśle prawdziwy email** na `jakub.majka.zg@gmail.com`
- ⏱️ Zajmuje: ~1 sekundę

#### 2. **Uruchom Prawdziwy Scraper**
```powershell
python main.py
```
**Co się stanie:**
- Pobierze prawdziwe dane z Forebet.com
- Przeanalizuje setki meczów (football, basketball, volleyball, hockey, handball)
- Znajdzie mecze z 60%+ szansą na sukces
- Wyśle email tylko jeśli znajdzie kwalifikujące się wydarzenia
- ⏱️ Zajmuje: 2-5 minut

#### 3. **Skonfiguruj Automatyzację** (opcjonalnie)
```
1. Idź do: https://github.com/JKM2828/Forebet-scrapper/settings/secrets/actions
2. Dodaj sekrety:
   - GMAIL_USER = jakub.majka.zg@gmail.com
   - GMAIL_PASSWORD = vurb tcai zaaq itjx
   - RECIPIENT_EMAIL = jakub.majka.zg@gmail.com
3. System będzie działać automatycznie codziennie o 2:00 UTC
```

---

## 📧 Sprawdź Email!

Po uruchomieniu `python demo.py` sprawdź swoją skrzynkę email.

**Otrzymasz wiadomość z:**
- 📊 Listą zakwalifikowanych meczów
- 🏆 Szczegółami każdego wydarzenia
- 📈 Statystykami H2H i formą drużyn
- 💰 Kursami bukmacherskimi
- ✅ Uzasadnieniem dlaczego mecz się kwalifikuje

---

## 🎯 Co dalej?

### Dostosuj ustawienia (opcjonalnie):

Edytuj plik `.env`:
```env
# Zmień próg (domyślnie 60%)
NOTIFICATION_THRESHOLD=55

# Zmień email odbiorcy
RECIPIENT_EMAIL=inny@email.com
```

### Uruchom testy:
```powershell
# Test połączenia Gmail
python test_smtp_minimal.py

# Test wysyłania emaila
python test_email.py
```

---

## ❓ Pytania?

Sprawdź pełną dokumentację:
- `FINAL_STATUS.md` - Status projektu i szczegóły techniczne
- `README.md` - Kompletna dokumentacja
- `SETUP.md` - Instrukcje instalacji

---

**Gotowe!** Twój Forebet Scraper działa! 🎉

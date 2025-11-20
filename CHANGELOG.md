# Changelog

## [1.0.0] - 2025-11-20

### Dodano
- ✅ Podstawowa struktura projektu
- ✅ Moduł konfiguracji i zarządzania sekretami
- ✅ System logowania z kolorowymi logami i rotacją
- ✅ Scraper Forebet z obsługą Selenium
- ✅ Analyzery: H2H, forma drużyn, home/away stats
- ✅ Pobieranie kursów (placeholder dla Flashscore)
- ✅ System filtrowania i kwalifikacji zdarzeń
- ✅ Wysyłanie powiadomień email przez Gmail
- ✅ Cache manager dla optymalizacji
- ✅ GitHub Actions workflow (cron 2:00 UTC)
- ✅ Dokumentacja (README, SETUP)
- ✅ Podstawowe testy jednostkowe

### TODO
- [ ] Implementacja rzeczywistego parsowania H2H z Forebet
- [ ] Implementacja pobierania formy drużyn z Forebet
- [ ] Reverse engineering Flashscore API dla kursów
- [ ] Dodanie LiveSport jako źródła kursów
- [ ] Rozszerzenie testów (coverage 80%+)
- [ ] Dodanie więcej sportów (baseball, rugby, cricket)
- [ ] Opcjonalna baza danych SQLite dla historii
- [ ] Dashboard webowy do przeglądania wyników
- [ ] Telegram/Slack notifications
- [ ] Docker containerization

### Znane Problemy
- Parsery H2H i formy wymagają dostosowania do rzeczywistej struktury HTML Forebet
- Flashscore fetcher to placeholder - wymaga implementacji
- Brak real-time danych meczowych (tylko prognozy)

---

## Konwencje wersjonowania
Używamy [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: Nowe funkcjonalności (backward compatible)
- PATCH: Bug fixes

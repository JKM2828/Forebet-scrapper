"""
Główny scraper Forebet - pobieranie zdarzeń sportowych.
"""
import time
import re
from typing import List, Dict, Optional, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import Settings, Sport
from ..data_management import get_logger, cache_manager

logger = get_logger(__name__)


class ForebtScraper:
    """Scraper dla strony Forebet - pobiera zdarzenia sportowe i prognozy."""
    
    def __init__(self, use_selenium: bool = True):
        """
        Inicjalizacja scrapera.
        
        Args:
            use_selenium: Czy używać Selenium (dla dynamicznego JS)
        """
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.driver = None
    
    def __enter__(self):
        """Context manager enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.close()
    
    def _init_driver(self):
        """Inicjalizuje WebDriver Selenium."""
        if self.driver:
            return
        
        try:
            chrome_options = Options()
            
            if Settings.HEADLESS_BROWSER:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={Settings.USER_AGENT}')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(Settings.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(Settings.PAGE_LOAD_TIMEOUT)
            
            logger.info("✓ WebDriver Selenium zainicjalizowany")
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji WebDriver: {e}")
            raise
    
    def close(self):
        """Zamyka połączenia i cleanup."""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("WebDriver zamknięty")
            except Exception as e:
                logger.error(f"Błąd zamykania WebDriver: {e}")
            finally:
                self.driver = None
        
        self.session.close()
    
    @retry(stop=stop_after_attempt(Settings.MAX_RETRIES), 
           wait=wait_exponential(multiplier=1, min=Settings.RETRY_DELAY, max=60))
    def fetch_events_by_sport(self, sport: Sport) -> List[Dict[str, Any]]:
        """
        Pobiera wszystkie zdarzenia dla danego sportu.
        
        Args:
            sport: Sport do pobrania
        
        Returns:
            Lista słowników z danymi zdarzeń
        """
        logger.info(f"🔍 Pobieranie zdarzeń: {sport.value}")
        
        # Sprawdź cache
        cache_key = f"events_{sport.value}_{datetime.now().strftime('%Y-%m-%d')}"
        cached_events = cache_manager.load(cache_key)
        
        if cached_events:
            logger.info(f"✓ Znaleziono w cache: {len(cached_events)} zdarzeń")
            return cached_events
        
        try:
            url = Settings.get_sport_url(sport)
            
            if self.use_selenium:
                events = self._fetch_with_selenium(url, sport)
            else:
                events = self._fetch_with_requests(url, sport)
            
            # Zapisz do cache
            if events:
                cache_manager.save(cache_key, events, ttl=1800)  # 30 minut
                logger.info(f"✓ Pobrano {len(events)} zdarzeń dla {sport.value}")
            else:
                logger.warning(f"⚠️  Brak zdarzeń dla {sport.value}")
            
            # Rate limiting
            time.sleep(Settings.REQUEST_DELAY)
            
            return events
            
        except Exception as e:
            logger.error(f"Błąd pobierania zdarzeń {sport.value}: {e}")
            raise
    
    def _fetch_with_requests(self, url: str, sport: Sport) -> List[Dict[str, Any]]:
        """Pobiera zdarzenia używając requests (statyczny HTML)."""
        response = self.session.get(url, timeout=Settings.FOREBET_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        return self._parse_events(soup, sport)
    
    def _fetch_with_selenium(self, url: str, sport: Sport) -> List[Dict[str, Any]]:
        """Pobiera zdarzenia używając Selenium (dynamiczny JS)."""
        self._init_driver()
        
        self.driver.get(url)
        
        # Czekaj na załadowanie tabeli z prognozami
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".schema, .rcnt, tr[data-tid]"))
            )
            time.sleep(2)  # Dodatkowy czas na JS
        except TimeoutException:
            logger.warning(f"Timeout czekania na elementy dla {sport.value}")
        
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        return self._parse_events(soup, sport)
    
    def _parse_events(self, soup: BeautifulSoup, sport: Sport) -> List[Dict[str, Any]]:
        """
        Parsuje HTML i ekstraktuje zdarzenia.
        
        Args:
            soup: BeautifulSoup object
            sport: Sport
        
        Returns:
            Lista zdarzeń
        """
        events = []
        
        # Znajdź wszystkie wiersze z meczami
        # Forebet używa różnych selektorów w zależności od sportu
        match_rows = soup.find_all('tr', attrs={'data-tid': True})
        
        if not match_rows:
            # Alternatywny selektor
            match_rows = soup.find_all('div', class_='rcnt')
        
        logger.debug(f"Znaleziono {len(match_rows)} wierszy do parsowania")
        
        for row in match_rows:
            try:
                event_data = self._parse_single_event(row, sport)
                if event_data:
                    events.append(event_data)
            except Exception as e:
                logger.debug(f"Błąd parsowania wiersza: {e}")
                continue
        
        return events
    
    def _parse_single_event(self, element, sport: Sport) -> Optional[Dict[str, Any]]:
        """
        Parsuje pojedyncze zdarzenie.
        
        Args:
            element: Element HTML (tr lub div)
            sport: Sport
        
        Returns:
            Słownik z danymi zdarzenia lub None
        """
        try:
            # Pobierz nazwę drużyn
            teams = self._extract_teams(element)
            if not teams:
                return None
            
            # Pobierz prawdopodobieństwa (1 / X / 2)
            probabilities = self._extract_probabilities(element)
            if not probabilities:
                return None
            
            # Pobierz link do szczegółów meczu
            match_url = self._extract_match_url(element)
            
            # Pobierz ligę
            league = self._extract_league(element)
            
            # Pobierz datę i czas
            match_time = self._extract_match_time(element)
            
            # ID meczu (z data-tid lub URL)
            match_id = element.get('data-tid') or self._extract_match_id_from_url(match_url)
            
            return {
                'match_id': match_id,
                'sport': sport.value,
                'home_team': teams['home'],
                'away_team': teams['away'],
                'probabilities': probabilities,
                'match_url': match_url,
                'league': league,
                'match_time': match_time,
                'scraped_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.debug(f"Błąd parsowania pojedynczego zdarzenia: {e}")
            return None
    
    def _extract_teams(self, element) -> Optional[Dict[str, str]]:
        """Ekstraktuje nazwy drużyn."""
        try:
            # Metoda 1: Szukaj span z klasą "homeTeam" i "awayTeam"
            home_team_elem = element.find('span', class_=re.compile(r'.*homeTeam.*|.*tnl.*|.*home.*', re.I))
            away_team_elem = element.find('span', class_=re.compile(r'.*awayTeam.*|.*tnl.*|.*away.*', re.I))
            
            if home_team_elem and away_team_elem:
                return {
                    'home': home_team_elem.get_text(strip=True),
                    'away': away_team_elem.get_text(strip=True)
                }
            
            # Metoda 2: Szukaj <a> z klasą team
            team_links = element.find_all('a', class_=re.compile(r'.*team.*', re.I))
            if len(team_links) >= 2:
                return {
                    'home': team_links[0].get_text(strip=True),
                    'away': team_links[1].get_text(strip=True)
                }
            
            # Metoda 3: Szukaj po kolejności <span>
            all_spans = element.find_all('span')
            if len(all_spans) >= 2:
                # Filtruj tylko te z tekstem
                text_spans = [s for s in all_spans if s.get_text(strip=True)]
                if len(text_spans) >= 2:
                    return {
                        'home': text_spans[0].get_text(strip=True),
                        'away': text_spans[1].get_text(strip=True)
                    }
            
            return None
            
        except Exception as e:
            logger.debug(f"Błąd ekstraktowania drużyn: {e}")
            return None
    
    def _extract_probabilities(self, element) -> Optional[Dict[str, float]]:
        """
        Ekstraktuje prawdopodobieństwa (1/X/2).
        
        Forebet format: <div class="fprc"><span class="fpr">40</span><span>38</span><span>22</span></div>
        """
        try:
            # Szukaj div z klasą "fprc" (forecast probability)
            prob_container = element.find('div', class_=re.compile(r'.*fprc.*|.*prob.*', re.I))
            
            if not prob_container:
                return None
            
            # Pobierz wszystkie spany z liczbami
            prob_spans = prob_container.find_all('span')
            
            if len(prob_spans) >= 3:
                try:
                    home_prob = float(prob_spans[0].get_text(strip=True))
                    draw_prob = float(prob_spans[1].get_text(strip=True))
                    away_prob = float(prob_spans[2].get_text(strip=True))
                    
                    return {
                        'home': home_prob,
                        'draw': draw_prob,
                        'away': away_prob,
                        'max': max(home_prob, draw_prob, away_prob),
                        'prediction': 'home' if home_prob == max(home_prob, draw_prob, away_prob) 
                                     else ('draw' if draw_prob == max(home_prob, draw_prob, away_prob) 
                                          else 'away')
                    }
                except (ValueError, IndexError) as e:
                    logger.debug(f"Błąd konwersji prawdopodobieństw: {e}")
                    return None
            
            return None
            
        except Exception as e:
            logger.debug(f"Błąd ekstraktowania prawdopodobieństw: {e}")
            return None
    
    def _extract_match_url(self, element) -> Optional[str]:
        """Ekstraktuje URL do szczegółów meczu."""
        try:
            # Szukaj <a> z href zawierającym "/matches/"
            link = element.find('a', href=re.compile(r'.*/matches/.*'))
            
            if link and link.get('href'):
                href = link.get('href')
                
                # Jeśli relatywny URL, dodaj bazowy
                if href.startswith('/'):
                    return f"{Settings.FOREBET_BASE_URL}{href}"
                
                return href
            
            return None
            
        except Exception as e:
            logger.debug(f"Błąd ekstraktowania URL meczu: {e}")
            return None
    
    def _extract_league(self, element) -> Optional[str]:
        """Ekstraktuje nazwę ligi."""
        try:
            # Szukaj elementu z ligą (często w title lub data attribute)
            league_elem = element.find(attrs={'title': True})
            
            if league_elem:
                return league_elem.get('title')
            
            return "Unknown League"
            
        except Exception:
            return "Unknown League"
    
    def _extract_match_time(self, element) -> Optional[str]:
        """Ekstraktuje czas meczu."""
        try:
            # Szukaj span z czasem (format: HH:MM)
            time_elem = element.find('span', class_=re.compile(r'.*time.*|.*date.*', re.I))
            
            if time_elem:
                return time_elem.get_text(strip=True)
            
            return None
            
        except Exception:
            return None
    
    def _extract_match_id_from_url(self, url: Optional[str]) -> Optional[str]:
        """Ekstraktuje ID meczu z URL."""
        if not url:
            return None
        
        # Format URL: .../matches/team1-team2-123456
        match = re.search(r'/matches/[^/]+-(\d+)', url)
        if match:
            return match.group(1)
        
        return None


# __init__.py marker
__all__ = ['ForebtScraper']

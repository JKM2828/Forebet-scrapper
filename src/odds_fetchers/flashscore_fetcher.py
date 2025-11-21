"""
Fetcher kursów z Flashscore API.
Pobiera kursy od Nordic Bet (bookmaker ID: 37).
"""
from typing import Dict, List, Optional, Any
import requests
import json
import re
from ..config import Settings
from ..data_management import get_logger, cache_manager

logger = get_logger(__name__)


class FlashscoreFetcher:
    """Pobieranie kursów bukmacherskich z Flashscore API."""
    
    # Nordic Bet bookmaker ID
    NORDIC_BET_ID = 37
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Settings.USER_AGENT,
            'Accept': '*/*',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8',
            'Referer': 'https://www.flashscore.pl/',
            'Origin': 'https://www.flashscore.pl',
            'X-Fsign': 'SW9D1eZo'  # Flashscore API signature
        })
        self.base_url = "https://d.flashscore.com/x/feed"
    
    def fetch_odds(self, match_id: str, home_team: str, away_team: str, sport: str = 'football') -> Optional[Dict[str, Any]]:
        """
        Pobiera kursy dla meczu od Nordic Bet.
        
        Args:
            match_id: ID meczu z Forebet
            home_team: Drużyna gospodarzy
            away_team: Drużyna gości
            sport: Sport (football, basketball, etc.)
        
        Returns:
            Słownik z kursami lub None
        """
        logger.debug(f"Pobieranie kursów Nordic Bet: {home_team} vs {away_team}")
        
        # Sprawdź cache
        cache_key = f"odds_{match_id}_nordicbet"
        cached_odds = cache_manager.load(cache_key)
        
        if cached_odds:
            logger.debug(f"✓ Kursy z cache dla {match_id}")
            return cached_odds
        
        try:
            # Najpierw musimy znaleźć flashscore_id meczu
            flashscore_id = self._search_match(home_team, away_team, sport)
            
            if not flashscore_id:
                logger.warning(f"Nie znaleziono meczu w Flashscore: {home_team} vs {away_team}")
                return self._empty_odds(match_id)
            
            # Pobierz kursy dla meczu
            odds_data = self._fetch_match_odds(flashscore_id)
            
            if odds_data and odds_data.get('has_odds'):
                logger.info(f"✓ Pobrano kursy Nordic Bet: 1:{odds_data['home_win']} X:{odds_data.get('draw', '-')} 2:{odds_data['away_win']}")
                
                # Cache na 30 minut
                cache_manager.save(cache_key, odds_data, ttl=1800)
                return odds_data
            else:
                logger.warning(f"Brak kursów Nordic Bet dla {match_id}")
                return self._empty_odds(match_id)
            
        except Exception as e:
            logger.error(f"Błąd pobierania kursów: {e}", exc_info=True)
            return self._empty_odds(match_id)
    
    def _search_match(self, home_team: str, away_team: str, sport: str) -> Optional[str]:
        """
        Wyszukuje mecz w Flashscore i zwraca jego ID.
        
        Args:
            home_team: Drużyna gospodarzy
            away_team: Drużyna gości
            sport: Sport
        
        Returns:
            Flashscore match ID lub None
        """
        try:
            # Flashscore search endpoint
            search_query = f"{home_team} {away_team}".replace(' ', '%20')
            search_url = f"https://www.flashscore.pl/wyszukiwanie/?q={search_query}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Parsuj HTML w poszukiwaniu ID meczu
            # Format: g_1_<match_id> w atrybucie id
            match = re.search(r'g_1_([A-Za-z0-9]+)', response.text)
            
            if match:
                flashscore_id = match.group(1)
                logger.debug(f"✓ Znaleziono Flashscore ID: {flashscore_id}")
                return flashscore_id
            
            return None
            
        except Exception as e:
            logger.error(f"Błąd wyszukiwania meczu: {e}")
            return None
    
    def _fetch_match_odds(self, flashscore_id: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera kursy dla meczu z Flashscore API.
        
        Args:
            flashscore_id: ID meczu w Flashscore
        
        Returns:
            Słownik z kursami lub None
        """
        try:
            # Flashscore odds endpoint
            # Format: /df_od_1_<match_id>_1_eu_1
            odds_url = f"{self.base_url}/df_od_1_{flashscore_id}_1_eu_1"
            
            response = self.session.get(odds_url, timeout=10)
            response.raise_for_status()
            
            # Parsuj odpowiedź API Flashscore
            # Format:特殊 format z separatorami ¬ i ~
            data = response.text
            
            # Szukaj kursów Nordic Bet (bookmaker ID: 37)
            odds = self._parse_flashscore_odds(data, self.NORDIC_BET_ID)
            
            if odds:
                return {
                    'source': 'flashscore_nordicbet',
                    'bookmaker': 'Nordic Bet',
                    'bookmaker_id': self.NORDIC_BET_ID,
                    'match_id': flashscore_id,
                    'has_odds': True,
                    'home_win': odds.get('home'),
                    'draw': odds.get('draw'),
                    'away_win': odds.get('away')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Błąd pobierania kursów z API: {e}")
            return None
    
    def _parse_flashscore_odds(self, data: str, bookmaker_id: int) -> Optional[Dict[str, Optional[float]]]:
        """
        Parsuje odpowiedź API Flashscore w poszukiwaniu kursów od danego bukmachera.
        
        Args:
            data: Surowa odpowiedź z API
            bookmaker_id: ID bukmachera (37 dla Nordic Bet)
        
        Returns:
            Słownik z kursami {home, draw, away} lub None
        """
        try:
            # Flashscore API format:
            # OD¬AA¬<bookmaker_id>¬<bookmaker_name>~OE¬<odds_home>¬<odds_draw>¬<odds_away>¬
            
            # Znajdź sekcję dla Nordic Bet
            lines = data.split('¬')
            
            for i, line in enumerate(lines):
                if line == str(bookmaker_id):
                    # Znaleziono Nordic Bet, teraz szukaj kursów
                    # Kursy są kilka linii dalej po znaczniku OE
                    for j in range(i, min(i + 20, len(lines))):
                        if lines[j] == 'OE' or lines[j].startswith('OE'):
                            # Następne 3 wartości to kursy: home, draw, away
                            try:
                                home_odd = float(lines[j + 1])
                                draw_odd = float(lines[j + 2]) if j + 2 < len(lines) else None
                                away_odd = float(lines[j + 3]) if j + 3 < len(lines) else None
                                
                                return {
                                    'home': home_odd,
                                    'draw': draw_odd,
                                    'away': away_odd
                                }
                            except (ValueError, IndexError) as e:
                                logger.debug(f"Błąd parsowania kursów: {e}")
                                continue
            
            logger.debug(f"Nie znaleziono kursów Nordic Bet w danych")
            return None
            
        except Exception as e:
            logger.error(f"Błąd parsowania kursów: {e}")
            return None
    
    def _empty_odds(self, match_id: str) -> Dict[str, Any]:
        """Zwraca puste kursy gdy nie można pobrać."""
        return {
            'source': 'flashscore_nordicbet',
            'bookmaker': 'Nordic Bet',
            'bookmaker_id': self.NORDIC_BET_ID,
            'match_id': match_id,
            'has_odds': False,
            'home_win': None,
            'draw': None,
            'away_win': None
        }
    
    def close(self):
        """Zamyka sesję."""
        self.session.close()


__all__ = ['FlashscoreFetcher']

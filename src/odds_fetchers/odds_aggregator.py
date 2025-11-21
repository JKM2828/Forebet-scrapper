"""
Agregator kursów z różnych źródeł.
"""
from typing import List, Dict, Any, Optional
from .flashscore_fetcher import FlashscoreFetcher
from ..data_management import get_logger

logger = get_logger(__name__)


class OddsAggregator:
    """Agreguje kursy z wielu źródeł."""
    
    def __init__(self):
        self.flashscore = FlashscoreFetcher()
    
    def aggregate_odds(self, match_id: str, home_team: str, away_team: str, sport: str = 'football') -> Dict[str, Any]:
        """
        Pobiera kursy Nordic Bet z Flashscore API.
        
        Args:
            match_id: ID meczu
            home_team: Drużyna gospodarzy
            away_team: Drużyna gości
            sport: Sport (football, basketball, etc.)
        
        Returns:
            Słownik z kursami Nordic Bet
        """
        # Pobierz z Flashscore (Nordic Bet)
        flashscore_odds = self.flashscore.fetch_odds(match_id, home_team, away_team, sport)
        
        if flashscore_odds and flashscore_odds.get('has_odds'):
            return flashscore_odds
        
        # Zwróć puste kursy jeśli nie znaleziono
        return {
            'source': 'flashscore_nordicbet',
            'bookmaker': 'Nordic Bet',
            'has_odds': False,
            'home_win': None,
            'draw': None,
            'away_win': None
        }
    
    def close(self):
        self.flashscore.close()


__all__ = ['OddsAggregator']

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
    
    def aggregate_odds(self, match_id: str, home_team: str, away_team: str) -> List[Dict[str, Any]]:
        """
        Pobiera i agreguje kursy z dostępnych źródeł.
        
        Returns:
            Lista słowników z kursami z różnych źródeł
        """
        all_odds = []
        
        # Pobierz z Flashscore
        flashscore_odds = self.flashscore.fetch_odds(match_id, home_team, away_team)
        if flashscore_odds:
            all_odds.append(flashscore_odds)
        
        # TODO: Dodać inne źródła (LiveSport, itp.)
        
        return all_odds
    
    def close(self):
        self.flashscore.close()


__all__ = ['OddsAggregator']

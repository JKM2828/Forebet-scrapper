"""
Analyzer formy drużyn - analiza ostatnich wyników.
"""
from typing import Dict, List, Any
from ..config import Settings
from ..data_management import get_logger

logger = get_logger(__name__)


class FormAnalyzer:
    """Analiza formy drużyn na podstawie ostatnich meczów."""
    
    def analyze_form(self, team: str, recent_matches: List[Dict]) -> Dict[str, Any]:
        """
        Analizuje formę drużyny.
        
        Args:
            team: Nazwa drużyny
            recent_matches: Lista ostatnich meczów
        
        Returns:
            Statystyki formy (punkty, W/D/L, trend)
        """
        if not recent_matches:
            return {'has_form': False, 'points': 0, 'matches_analyzed': 0}
        
        points = 0
        wins = draws = losses = 0
        
        for match in recent_matches[:Settings.MATCHES_TO_ANALYZE]:
            result = match.get('result', 'U')
            
            if result == 'W':
                points += 3
                wins += 1
            elif result == 'D':
                points += 1
                draws += 1
            elif result == 'L':
                losses += 1
        
        return {
            'has_form': True,
            'points': points,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'matches_analyzed': len(recent_matches[:Settings.MATCHES_TO_ANALYZE]),
            'avg_points': round(points / Settings.MATCHES_TO_ANALYZE, 2),
            'record': f"{wins}W-{draws}D-{losses}L"
        }


__all__ = ['FormAnalyzer']

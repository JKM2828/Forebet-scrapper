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
            recent_matches: Lista ostatnich meczów (z forebet_scraper.fetch_team_form)
        
        Returns:
            Statystyki formy (punkty, W/D/L, trend)
        """
        if not recent_matches:
            logger.debug(f"Brak danych formy dla {team}")
            return {
                'has_form': False, 
                'points': 0, 
                'matches_analyzed': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'record': 'N/A',
                'display': 'N/A (0 pkt)'
            }
        
        points = 0
        wins = draws = losses = 0
        
        # Analizuj maksymalnie MATCHES_TO_ANALYZE meczów
        matches_to_check = recent_matches[:Settings.MATCHES_TO_ANALYZE]
        
        for match in matches_to_check:
            result = match.get('result', 'U')
            
            if result == 'W':
                points += 3
                wins += 1
            elif result == 'D':
                points += 1
                draws += 1
            elif result == 'L':
                losses += 1
        
        matches_count = len(matches_to_check)
        avg_points = round(points / matches_count, 2) if matches_count > 0 else 0
        
        logger.debug(f"Forma {team}: {wins}W-{draws}D-{losses}L = {points} pkt z {matches_count} meczów")
        
        return {
            'has_form': True,
            'points': points,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'matches_analyzed': matches_count,
            'avg_points': avg_points,
            'record': f"{wins}W-{draws}D-{losses}L",
            'display': f"{wins}W-{draws}D-{losses}L ({points} pkt)"
        }


__all__ = ['FormAnalyzer']

"""
Analyzer statystyk u siebie/na wyjeździe.
"""
from typing import Dict, List, Any
from ..data_management import get_logger

logger = get_logger(__name__)


class HomeAwayAnalyzer:
    """Analiza statystyk drużyn u siebie i na wyjeździe."""
    
    def analyze_home_record(self, team: str, home_matches: List[Dict]) -> Dict[str, Any]:
        """
        Analizuje formę drużyny u siebie.
        
        Args:
            team: Nazwa drużyny
            home_matches: Lista meczów u siebie
        
        Returns:
            Statystyki meczów u siebie
        """
        return self._analyze_matches(team, home_matches, "home")
    
    def analyze_away_record(self, team: str, away_matches: List[Dict]) -> Dict[str, Any]:
        """
        Analizuje formę drużyny na wyjeździe.
        
        Args:
            team: Nazwa drużyny
            away_matches: Lista meczów na wyjeździe
        
        Returns:
            Statystyki meczów na wyjeździe
        """
        return self._analyze_matches(team, away_matches, "away")
    
    def _analyze_matches(self, team: str, matches: List[Dict], venue: str) -> Dict[str, Any]:
        """
        Analizuje mecze.
        
        Args:
            team: Nazwa drużyny
            matches: Lista meczów
            venue: "home" lub "away"
        
        Returns:
            Statystyki meczów
        """
        if not matches:
            logger.debug(f"Brak danych {venue} dla {team}")
            return {
                'has_record': False, 
                'points': 0, 
                'venue': venue,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'record': 'N/A',
                'display': 'N/A (0 pkt)'
            }
        
        points = wins = draws = losses = 0
        
        # Analizuj max 6 ostatnich meczów
        matches_to_check = matches[:6]
        
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
        venue_name = "u siebie" if venue == "home" else "na wyjeździe"
        
        logger.debug(f"Forma {team} {venue_name}: {wins}W-{draws}D-{losses}L = {points} pkt z {matches_count} meczów")
        
        return {
            'has_record': True,
            'venue': venue,
            'points': points,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'matches_analyzed': matches_count,
            'record': f"{wins}W-{draws}D-{losses}L",
            'display': f"{wins}W-{draws}D-{losses}L ({points} pkt)"
        }


__all__ = ['HomeAwayAnalyzer']

"""
Analyzer statystyk u siebie/na wyjeździe.
"""
from typing import Dict, List, Any
from ..data_management import get_logger

logger = get_logger(__name__)


class HomeAwayAnalyzer:
    """Analiza statystyk drużyn u siebie i na wyjeździe."""
    
    def analyze_home_record(self, team: str, home_matches: List[Dict]) -> Dict[str, Any]:
        """Analizuje formę drużyny u siebie."""
        return self._analyze_matches(home_matches, "home")
    
    def analyze_away_record(self, team: str, away_matches: List[Dict]) -> Dict[str, Any]:
        """Analizuje formę drużyny na wyjeździe."""
        return self._analyze_matches(away_matches, "away")
    
    def _analyze_matches(self, matches: List[Dict], venue: str) -> Dict[str, Any]:
        """Analizuje mecze."""
        if not matches:
            return {'has_record': False, 'points': 0, 'venue': venue}
        
        points = wins = draws = losses = 0
        
        for match in matches[:6]:
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
            'has_record': True,
            'venue': venue,
            'points': points,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'record': f"{wins}W-{draws}D-{losses}L"
        }


__all__ = ['HomeAwayAnalyzer']

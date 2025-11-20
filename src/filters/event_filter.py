"""
Filtr zdarzeń - kwalifikacja na podstawie kryteriów.
"""
from typing import Dict, Any, Tuple, Optional
from ..config import Settings
from ..data_management import get_logger

logger = get_logger(__name__)


class EventFilter:
    """Filtrowanie i kwalifikacja zdarzeń."""
    
    @staticmethod
    def qualify_event(event: Dict[str, Any], analysis: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Sprawdza czy zdarzenie spełnia wszystkie kryteria kwalifikacji.
        
        Args:
            event: Dane zdarzenia
            analysis: Dane analityczne (H2H, forma, home/away, kursy)
        
        Returns:
            (qualified, reason) - True jeśli kwalifikuje się, powód decyzji
        """
        # Kryterium 1: Przewaga matematyczna ≥ 60%
        max_prob = event.get('probabilities', {}).get('max', 0)
        
        if max_prob < Settings.NOTIFICATION_THRESHOLD:
            return False, f"Przewaga {max_prob}% < {Settings.NOTIFICATION_THRESHOLD}%"
        
        # Kryterium 2: Historia H2H (jeśli dostępna)
        h2h = analysis.get('h2h', {})
        
        if h2h.get('has_history', False):
            if not h2h.get('meets_threshold', False):
                win_rate = h2h.get('home_win_rate', 0) * 100
                return False, f"H2H win rate {win_rate:.1f}% < 60%"
        
        # Kryterium 3: Forma ogólna
        home_form = analysis.get('home_form', {})
        away_form = analysis.get('away_form', {})
        
        if home_form.get('has_form') and away_form.get('has_form'):
            home_points = home_form.get('points', 0)
            away_points = away_form.get('points', 0)
            
            if home_points <= away_points:
                return False, f"Forma: {home_points}pkt vs {away_points}pkt - brak przewagi"
        
        # Kryterium 4: Home/Away
        home_home = analysis.get('home_home_record', {})
        away_away = analysis.get('away_away_record', {})
        
        if home_home.get('has_record') and away_away.get('has_record'):
            home_home_points = home_home.get('points', 0)
            away_away_points = away_away.get('points', 0)
            
            if home_home_points <= away_away_points:
                return False, f"Home/Away: {home_home_points}pkt vs {away_away_points}pkt - brak przewagi"
        
        # Kryterium 5: Kursy dostępne
        odds = analysis.get('odds', [])
        if not odds or len(odds) == 0:
            return False, "Brak dostępnych kursów"
        
        # Wszystkie kryteria spełnione
        return True, "Wszystkie kryteria spełnione ✓"


__all__ = ['EventFilter']

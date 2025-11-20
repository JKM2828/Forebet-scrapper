"""
Analyzer H2H (Head-to-Head) - analiza bezpośrednich spotkań drużyn.
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..config import Settings
from ..data_management import get_logger, cache_manager

logger = get_logger(__name__)


class HeadToHeadAnalyzer:
    """Analiza historii bezpośrednich starć między drużynami."""
    
    def __init__(self, use_selenium: bool = False):
        """
        Inicjalizacja analyzera H2H.
        
        Args:
            use_selenium: Czy używać Selenium
        """
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Settings.USER_AGENT})
        self.driver = None
    
    def analyze_h2h(self, home_team: str, away_team: str, match_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analizuje historię H2H między dwiema drużynami.
        
        Args:
            home_team: Nazwa drużyny gospodarzy
            away_team: Nazwa drużyny gości
            match_url: URL do strony meczu na Forebet (jeśli dostępny)
        
        Returns:
            Słownik z analizą H2H
        """
        logger.debug(f"Analiza H2H: {home_team} vs {away_team}")
        
        # Sprawdź cache
        cache_key = f"h2h_{home_team}_{away_team}"
        cached_h2h = cache_manager.load(cache_key)
        
        if cached_h2h:
            logger.debug("✓ H2H znaleziono w cache")
            return cached_h2h
        
        try:
            # Pobierz historię meczów
            h2h_matches = self._fetch_h2h_matches(home_team, away_team, match_url)
            
            if not h2h_matches:
                logger.warning(f"Brak historii H2H dla {home_team} vs {away_team}")
                return {
                    'has_history': False,
                    'total_matches': 0,
                    'home_wins': 0,
                    'draws': 0,
                    'away_wins': 0,
                    'home_win_rate': 0.0,
                    'matches': []
                }
            
            # Oblicz statystyki
            stats = self._calculate_h2h_stats(h2h_matches, home_team)
            
            # Zapisz do cache (24h)
            cache_manager.save(cache_key, stats, ttl=86400)
            
            return stats
            
        except Exception as e:
            logger.error(f"Błąd analizy H2H: {e}")
            return {
                'has_history': False,
                'total_matches': 0,
                'error': str(e)
            }
    
    def _fetch_h2h_matches(self, home_team: str, away_team: str, match_url: Optional[str]) -> List[Dict]:
        """Pobiera historię meczów H2H."""
        if match_url:
            # Pobierz z strony meczu na Forebet
            return self._fetch_h2h_from_match_page(match_url)
        else:
            # Brak URL - nie można pobrać
            logger.debug("Brak URL meczu - nie można pobrać H2H")
            return []
    
    def _fetch_h2h_from_match_page(self, match_url: str) -> List[Dict]:
        """Pobiera H2H ze strony szczegółów meczu."""
        try:
            response = self.session.get(match_url, timeout=Settings.FOREBET_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Znajdź sekcję H2H (przykładowe selektory - trzeba dostosować do rzeczywistej struktury)
            h2h_section = soup.find('div', class_=re.compile(r'h2h', re.IGNORECASE))
            
            if not h2h_section:
                logger.debug("Nie znaleziono sekcji H2H na stronie")
                return []
            
            matches = []
            
            # Parsuj mecze (trzeba dostosować do struktury Forebet)
            match_rows = h2h_section.find_all('tr', class_=re.compile(r'match', re.IGNORECASE))
            
            for row in match_rows[:Settings.H2H_MATCHES_TO_ANALYZE]:
                try:
                    match_data = self._parse_h2h_match(row)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.debug(f"Błąd parsowania meczu H2H: {e}")
                    continue
            
            return matches
            
        except Exception as e:
            logger.error(f"Błąd pobierania H2H z {match_url}: {e}")
            return []
    
    def _parse_h2h_match(self, row) -> Optional[Dict]:
        """Parsuje pojedynczy mecz H2H."""
        try:
            # Przykładowa struktura - trzeba dostosować
            date_elem = row.find('span', class_='date')
            score_elem = row.find('span', class_='score')
            teams_elems = row.find_all('a', class_='team')
            
            if not all([date_elem, score_elem, len(teams_elems) >= 2]):
                return None
            
            return {
                'date': date_elem.get_text(strip=True),
                'home_team': teams_elems[0].get_text(strip=True),
                'away_team': teams_elems[1].get_text(strip=True),
                'score': score_elem.get_text(strip=True),
            }
            
        except Exception as e:
            logger.debug(f"Błąd parsowania meczu: {e}")
            return None
    
    def _calculate_h2h_stats(self, matches: List[Dict], home_team: str) -> Dict[str, Any]:
        """Oblicza statystyki H2H."""
        total_matches = len(matches)
        home_wins = 0
        draws = 0
        away_wins = 0
        
        for match in matches:
            result = self._determine_result(match, home_team)
            
            if result == 'W':
                home_wins += 1
            elif result == 'D':
                draws += 1
            elif result == 'L':
                away_wins += 1
        
        home_win_rate = home_wins / total_matches if total_matches > 0 else 0.0
        
        return {
            'has_history': True,
            'total_matches': total_matches,
            'home_wins': home_wins,
            'draws': draws,
            'away_wins': away_wins,
            'home_win_rate': round(home_win_rate, 3),
            'meets_threshold': home_win_rate >= Settings.H2H_MIN_WIN_RATE,
            'matches': matches
        }
    
    def _determine_result(self, match: Dict, home_team: str) -> str:
        """
        Określa wynik meczu z perspektywy home_team.
        
        Returns:
            'W' (win), 'D' (draw), 'L' (loss)
        """
        try:
            score = match.get('score', '')
            
            # Format: "2-1" lub "2 - 1"
            parts = score.replace(' ', '').split('-')
            
            if len(parts) != 2:
                return 'U'  # Unknown
            
            home_goals = int(parts[0])
            away_goals = int(parts[1])
            
            # Sprawdź czy home_team był gospodarzem w tym meczu
            is_home = home_team.lower() in match.get('home_team', '').lower()
            
            if home_goals > away_goals:
                return 'W' if is_home else 'L'
            elif home_goals < away_goals:
                return 'L' if is_home else 'W'
            else:
                return 'D'
                
        except Exception:
            return 'U'
    
    def close(self):
        """Cleanup."""
        self.session.close()
        if self.driver:
            self.driver.quit()


__all__ = ['HeadToHeadAnalyzer']

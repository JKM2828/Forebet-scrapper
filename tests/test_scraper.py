"""
Przykładowy test dla forebet_scraper.
"""
import pytest
from src.scrapers import ForebtScraper
from src.config import Sport


def test_scraper_initialization():
    """Test inicjalizacji scrapera."""
    scraper = ForebtScraper(use_selenium=False)
    assert scraper is not None
    scraper.close()


def test_extract_teams_logic():
    """Test logiki ekstraktowania drużyn."""
    # TODO: Dodać mock HTML i testy parsowania
    pass


def test_extract_probabilities_logic():
    """Test logiki ekstraktowania prawdopodobieństw."""
    # TODO: Dodać mock HTML i testy parsowania
    pass


if __name__ == "__main__":
    pytest.main([__file__])

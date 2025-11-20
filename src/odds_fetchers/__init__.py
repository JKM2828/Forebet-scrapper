"""Inicjalizacja modułu odds_fetchers."""
from .flashscore_fetcher import FlashscoreFetcher
from .odds_aggregator import OddsAggregator

__all__ = ["FlashscoreFetcher", "OddsAggregator"]

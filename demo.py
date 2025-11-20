"""
Demo - Symulacja działania Forebet Scraper z przykładowymi danymi.

Ten skrypt symuluje kompletne działanie scrapera z wygenerowanymi danymi
demonstracyjnymi, aby pokazać pełny przepływ: scraping → analiza → filtrowanie → email.
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.config import Settings, secrets
from src.filters import EventFilter
from src.notifiers import EmailSender
from src.data_management import get_logger

logger = get_logger(__name__)

# Przykładowe zdarzenia z Forebet (symulowane)
DEMO_EVENTS = [
    {
        "match_id": "demo_001",
        "sport": "football",
        "home_team": "Manchester City",
        "away_team": "Liverpool",
        "match_time": (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
        "prediction": {
            "home": 45.0,
            "draw": 28.0,
            "away": 27.0,
            "max": 45.0,
            "prediction": "home"
        },
        "head_to_head": {
            "total_matches": 10,
            "home_wins": 6,
            "draws": 2,
            "away_wins": 2,
            "home_win_rate": 60.0
        },
        "form": {
            "home": {
                "last_6_overall": "WWDWWL",
                "last_6_home": "WWWWWD",
                "points_overall": 16,
                "points_home": 17
            },
            "away": {
                "last_6_overall": "WLWDLL",
                "last_6_away": "LWDLLL",
                "points_overall": 10,
                "points_away": 4
            }
        },
        "odds": {
            "home_win": 2.10,
            "draw": 3.50,
            "away_win": 3.80,
            "best_value": "home_win",
            "implied_probability": 47.6
        },
        "qualifying_reasons": [
            "✓ Prawdopodobieństwo matematyczne: 45.0% (próg: 40%)",
            "✓ H2H: 60.0% wygranych gospodarzy",
            "✓ Forma domowa: 17/18 punktów w ostatnich 6 meczach",
            "✓ Słaba forma gości na wyjeździe: 4/18 punktów"
        ]
    },
    {
        "match_id": "demo_002",
        "sport": "basketball",
        "home_team": "Los Angeles Lakers",
        "away_team": "Golden State Warriors",
        "match_time": (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
        "prediction": {
            "home": 62.0,
            "away": 38.0,
            "max": 62.0,
            "prediction": "home"
        },
        "head_to_head": {
            "total_matches": 15,
            "home_wins": 10,
            "draws": 0,
            "away_wins": 5,
            "home_win_rate": 66.7
        },
        "form": {
            "home": {
                "last_6_overall": "WWWWLW",
                "last_6_home": "WWWWWW",
                "points_overall": 15,
                "points_home": 18
            },
            "away": {
                "last_6_overall": "LWLWLL",
                "last_6_away": "LLLLWL",
                "points_overall": 8,
                "points_away": 4
            }
        },
        "odds": {
            "home_win": 1.65,
            "away_win": 2.30,
            "best_value": "home_win",
            "implied_probability": 60.6
        },
        "qualifying_reasons": [
            "✓ Prawdopodobieństwo matematyczne: 62.0% (próg: 60%)",
            "✓ H2H: 66.7% wygranych gospodarzy",
            "✓ Perfekcyjna forma domowa: 18/18 punktów",
            "✓ Tragiczna forma gości na wyjeździe: 4/18 punktów"
        ]
    },
    {
        "match_id": "demo_003",
        "sport": "volleyball",
        "home_team": "Zenit Kazan",
        "away_team": "Dinamo Moscow",
        "match_time": (datetime.now() + timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M"),
        "prediction": {
            "home": 68.0,
            "away": 32.0,
            "max": 68.0,
            "prediction": "home"
        },
        "head_to_head": {
            "total_matches": 8,
            "home_wins": 6,
            "draws": 0,
            "away_wins": 2,
            "home_win_rate": 75.0
        },
        "form": {
            "home": {
                "last_6_overall": "WWWWWW",
                "last_6_home": "WWWWWW",
                "points_overall": 18,
                "points_home": 18
            },
            "away": {
                "last_6_overall": "WLWLWL",
                "last_6_away": "LWLLWL",
                "points_overall": 9,
                "points_away": 5
            }
        },
        "odds": {
            "home_win": 1.45,
            "away_win": 2.85,
            "best_value": "home_win",
            "implied_probability": 69.0
        },
        "qualifying_reasons": [
            "✓ Prawdopodobieństwo matematyczne: 68.0% (próg: 60%)",
            "✓ H2H: 75.0% wygranych gospodarzy",
            "✓ Idealna passa domowa: 6/6 wygranych",
            "✓ Słaba forma gości: tylko 5/18 punktów na wyjeździe"
        ]
    }
]


def demo_full_workflow():
    """Demonstracja pełnego przepływu pracy scrapera."""
    logger.info("=" * 70)
    logger.info("🎬 DEMO - Forebet Scraper - Kompletny Przepływ")
    logger.info("=" * 70)
    logger.info("")
    
    # 1. Symulacja scraping
    logger.info("📥 Krok 1: Scraping danych z Forebet (symulowane)")
    logger.info(f"   Pobrano {len(DEMO_EVENTS)} zdarzeń z różnych sportów")
    logger.info("")
    
    # 2. Filtrowanie
    logger.info("🔍 Krok 2: Filtrowanie według kryteriów")
    event_filter = EventFilter()
    
    qualified_events = []
    for event in DEMO_EVENTS:
        logger.info(f"   Analiza: {event['home_team']} vs {event['away_team']}")
        
        # Sprawdź czy spełnia kryteria
        # EventFilter używa metody statycznej qualify_event(event, analysis)
        # W demo nie mamy pełnej analizy, więc używamy uproszczonego sprawdzenia
        if event['prediction']['max'] >= Settings.NOTIFICATION_THRESHOLD:
            qualified_events.append(event)
            logger.info(f"      ✅ KWALIFIKUJE SIĘ (max prob: {event['prediction']['max']}%)")
        else:
            logger.info(f"      ❌ Odrzucone (max prob: {event['prediction']['max']}%)")
    
    logger.info("")
    logger.info(f"✓ Zakwalifikowane zdarzenia: {len(qualified_events)}/{len(DEMO_EVENTS)}")
    logger.info("")
    
    # 3. Szczegóły zakwalifikowanych zdarzeń
    if qualified_events:
        logger.info("📋 Krok 3: Szczegóły zakwalifikowanych zdarzeń")
        for i, event in enumerate(qualified_events, 1):
            logger.info(f"\n   [{i}] {event['sport'].upper()}: {event['home_team']} vs {event['away_team']}")
            logger.info(f"       Czas: {event['match_time']}")
            logger.info(f"       Przewidywanie: {event['prediction']['prediction']} ({event['prediction']['max']}%)")
            logger.info(f"       H2H: {event['head_to_head']['home_win_rate']}% wygranych gospodarzy")
            logger.info(f"       Kursy: Gospod. {event['odds']['home_win']} | Remis {event['odds'].get('draw', '-')} | Goście {event['odds']['away_win']}")
            logger.info("       Powody kwalifikacji:")
            for reason in event['qualifying_reasons']:
                logger.info(f"         {reason}")
        
        logger.info("")
        
        # 4. Wysyłanie emaila
        logger.info("📧 Krok 4: Wysyłanie powiadomienia email")
        
        if secrets.gmail_user and secrets.gmail_password:
            try:
                email_sender = EmailSender()
                success = email_sender.send_qualified_events(qualified_events)
                
                if success:
                    logger.info(f"   ✅ Email wysłany pomyślnie do: {secrets.recipient_email}")
                else:
                    logger.warning("   ⚠️ Nie udało się wysłać emaila")
            except Exception as e:
                logger.error(f"   ❌ Błąd wysyłania emaila: {e}")
        else:
            logger.warning("   ⚠️ Brak konfiguracji Gmail - email nie został wysłany")
            logger.info("   💡 Skonfiguruj GMAIL_USER i GMAIL_PASSWORD w pliku .env")
    else:
        logger.info("ℹ️  Brak zdarzeń spełniających kryteria - email nie zostanie wysłany")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ DEMO ZAKOŃCZONE")
    logger.info("=" * 70)
    logger.info("")
    logger.info("📝 Uwagi:")
    logger.info("   • To demo używa symulowanych danych")
    logger.info("   • Uruchom 'python main.py' aby użyć prawdziwych danych z Forebet")
    logger.info("   • Skonfiguruj GitHub Actions do automatycznego uruchamiania")
    logger.info("")


if __name__ == "__main__":
    try:
        demo_full_workflow()
    except Exception as e:
        logger.error(f"Błąd podczas demo: {e}", exc_info=True)
        exit(1)

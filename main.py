"""
Forebet Scraper - Główny orchestrator
Automatyczne monitorowanie zdarzeń sportowych z Forebet.
"""
import sys
import time
import smtplib
from datetime import datetime
from typing import List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import Settings, Sport, secrets
from src.data_management import get_logger, Logger, cache_manager
from src.scrapers import ForebtScraper
from src.analyzers import HeadToHeadAnalyzer, FormAnalyzer, HomeAwayAnalyzer
from src.odds_fetchers import OddsAggregator
from src.filters import EventFilter
from src.notifiers import EmailSender

# Konfiguruj root logger
Logger.setup_root_logger()
logger = get_logger(__name__)


def main():
    """Główna funkcja orchestratora."""
    logger.info("=" * 70)
    logger.info("🚀 Forebet Scraper uruchomiony")
    logger.info(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    try:
        # Waliduj sekrety
        logger.info("🔐 Walidacja sekretów...")
        secrets.validate_required_secrets()
        logger.info("✓ Sekrety zwalidowane")
        
        # Cleanup wygasłego cache
        logger.info("🧹 Czyszczenie wygasłego cache...")
        expired = cache_manager.cleanup_expired()
        if expired > 0:
            logger.info(f"✓ Usunięto {expired} wygasłych plików cache")
        
        # Lista sportów do analizy
        sports_to_analyze = Settings.SUPPORTED_SPORTS
        logger.info(f"🎯 Sporty do analizy: {', '.join([s.value for s in sports_to_analyze])}")
        
        # Zbierz wszystkie zdarzenia
        all_events = []
        
        with ForebtScraper(use_selenium=True) as scraper:
            for sport in sports_to_analyze:
                try:
                    logger.info(f"\n{'─' * 70}")
                    logger.info(f"🏆 Przetwarzanie sportu: {sport.value.upper()}")
                    logger.info(f"{'─' * 70}")
                    
                    events = scraper.fetch_events_by_sport(sport)
                    
                    if not events:
                        logger.warning(f"⚠️  Brak zdarzeń dla {sport.value}")
                        continue
                    
                    # Filtruj po przewadze matematycznej
                    filtered_events = [
                        e for e in events 
                        if e.get('probabilities', {}).get('max', 0) >= Settings.NOTIFICATION_THRESHOLD
                    ]
                    
                    logger.info(f"✓ Znaleziono {len(events)} zdarzeń, {len(filtered_events)} z przewagą ≥{Settings.NOTIFICATION_THRESHOLD}%")
                    
                    all_events.extend(filtered_events)
                    
                except Exception as e:
                    logger.error(f"❌ Błąd przetwarzania {sport.value}: {e}")
                    continue
        
        if not all_events:
            logger.warning("\n⚠️  Brak zdarzeń spełniających kryterium przewagi matematycznej")
            send_no_events_notification()
            return 0
        
        logger.info(f"\n📊 Łącznie zdarzeń do dalszej analizy: {len(all_events)}")
        
        # Analiza i kwalifikacja zdarzeń
        qualified_events = analyze_and_qualify_events(all_events)
        
        if not qualified_events:
            logger.warning("\n⚠️  Brak zdarzeń spełniających wszystkie kryteria kwalifikacji")
            send_no_events_notification()
            return 0
        
        logger.info(f"\n✅ Kwalifikowanych zdarzeń: {len(qualified_events)}")
        
        # Wysłanie emaila
        logger.info(f"\n{'=' * 70}")
        logger.info("📧 Wysyłanie powiadomienia email...")
        logger.info(f"{'=' * 70}")
        
        email_sender = EmailSender()
        success = email_sender.send_qualified_events(qualified_events)
        
        if success:
            logger.info("✅ Email wysłany pomyślnie!")
        else:
            logger.error("❌ Błąd wysyłania emaila")
            return 1
        
        # Podsumowanie
        logger.info(f"\n{'=' * 70}")
        logger.info("📊 PODSUMOWANIE")
        logger.info(f"{'=' * 70}")
        logger.info(f"Sportów przeanalizowanych: {len(sports_to_analyze)}")
        logger.info(f"Zdarzeń znalezionych: {len(all_events)}")
        logger.info(f"Zdarzeń kwalifikowanych: {len(qualified_events)}")
        logger.info(f"{'=' * 70}")
        logger.info("✅ Forebet Scraper zakończony pomyślnie")
        logger.info(f"{'=' * 70}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Krytyczny błąd: {e}", exc_info=True)
        return 1


def analyze_and_qualify_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analizuje i kwalifikuje zdarzenia.
    
    Args:
        events: Lista zdarzeń do analizy
    
    Returns:
        Lista kwalifikowanych zdarzeń z analizą
    """
    qualified = []
    
    h2h_analyzer = HeadToHeadAnalyzer()
    form_analyzer = FormAnalyzer()
    home_away_analyzer = HomeAwayAnalyzer()
    odds_aggregator = OddsAggregator()
    event_filter = EventFilter()
    
    logger.info(f"\n{'─' * 70}")
    logger.info("🔍 Analiza i kwalifikacja zdarzeń...")
    logger.info(f"{'─' * 70}\n")
    
    # Utwórz scraper do pobierania szczegółów (forma)
    scraper = ForebtScraper(use_selenium=True)
    scraper._init_driver()
    
    try:
        for i, event in enumerate(events, 1):
            try:
                home_team = event.get('home_team', '')
                away_team = event.get('away_team', '')
                match_url = event.get('match_url', '')
                match_id = event.get('match_id', '')
                
                logger.info(f"[{i}/{len(events)}] Analiza: {home_team} vs {away_team}")
                
                # H2H Analysis
                h2h = h2h_analyzer.analyze_h2h(home_team, away_team, match_url)
                
                # Pobierz formę drużyn z detali meczu
                logger.debug(f"   Pobieranie formy drużyn...")
                team_form_data = scraper.fetch_team_form(match_url)
                
                home_form = form_analyzer.analyze_form(home_team, team_form_data.get('home_form', []))
                away_form = form_analyzer.analyze_form(away_team, team_form_data.get('away_form', []))
                
                # Home/Away Analysis (używamy tej samej formy - uproszczenie)
                # TODO: W przyszłości można dodać osobne pobieranie statystyk home/away
                home_home_record = home_away_analyzer.analyze_home_record(home_team, team_form_data.get('home_form', []))
                away_away_record = home_away_analyzer.analyze_away_record(away_team, team_form_data.get('away_form', []))
                
                # Odds
                odds = odds_aggregator.aggregate_odds(match_id, home_team, away_team)
                
                # Kompletna analiza
                analysis = {
                    'h2h': h2h,
                    'home_form': home_form,
                    'away_form': away_form,
                    'home_home_record': home_home_record,
                    'away_away_record': away_away_record,
                    'odds': odds
                }
                
                # Kwalifikacja
                is_qualified, reason = event_filter.qualify_event(event, analysis)
                
                if is_qualified:
                    logger.info(f"   ✅ KWALIFIKOWANE: {reason}")
                    qualified.append({
                        'event': event,
                        'analysis': analysis,
                        'qualification_reason': reason
                    })
                else:
                    logger.debug(f"   ❌ Odrzucone: {reason}")
                
            except Exception as e:
                logger.error(f"   ❌ Błąd analizy: {e}")
                continue
    
    finally:
        # Cleanup
        scraper.close()
        h2h_analyzer.close()
        odds_aggregator.close()
    
    return qualified


def send_no_events_notification():
    """Wysyła powiadomienie o braku kwalifikowanych zdarzeń."""
    try:
        email_sender = EmailSender()
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Forebet Scraper - Brak kwalifikowanych zdarzeń</h2>
            <p><strong>Data:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Dzisiaj nie znaleziono żadnych zdarzeń spełniających wszystkie kryteria kwalifikacji.</p>
            <p style="color: #7f8c8d; font-size: 0.9em;">Wygenerowane automatycznie przez Forebet Scraper</p>
        </body>
        </html>
        """
        
        message = MIMEMultipart('alternative')
        message['Subject'] = "Forebet Scraper - Brak kwalifikowanych zdarzeń"
        message['From'] = email_sender.sender_email
        message['To'] = email_sender.recipient_email
        
        message.attach(MIMEText(html, 'html', 'utf-8'))
        
        with smtplib.SMTP(email_sender.smtp_server, email_sender.smtp_port) as server:
            if Settings.USE_TLS:
                server.starttls()
            server.login(email_sender.sender_email, email_sender.sender_password)
            server.sendmail(email_sender.sender_email, email_sender.recipient_email, message.as_string())
        
        logger.info("📧 Wysłano powiadomienie o braku zdarzeń")
        
    except Exception as e:
        logger.error(f"Błąd wysyłania powiadomienia: {e}")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

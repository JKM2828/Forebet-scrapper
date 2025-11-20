"""
Email sender - wysyłanie powiadomień przez Gmail SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from datetime import datetime

from ..config import Settings, secrets
from ..data_management import get_logger

logger = get_logger(__name__)


class EmailSender:
    """Wysyłanie emaili przez Gmail SMTP."""
    
    def __init__(self):
        self.smtp_server = Settings.SMTP_SERVER
        self.smtp_port = Settings.SMTP_PORT
        self.sender_email = secrets.gmail_user
        self.sender_password = secrets.gmail_password
        self.recipient_email = secrets.recipient_email
    
    def send_qualified_events(self, qualified_events: List[Dict[str, Any]]) -> bool:
        """
        Wysyła email z kwalifikowanymi zdarzeniami.
        
        Args:
            qualified_events: Lista kwalifikowanych zdarzeń
        
        Returns:
            True jeśli wysłano pomyślnie
        """
        if not qualified_events:
            logger.info("Brak kwalifikowanych zdarzeń do wysłania")
            return False
        
        try:
            subject = f"Forebet Scraper - {len(qualified_events)} kwalifikowanych zdarzeń"
            html_content = self._generate_html(qualified_events)
            
            return self._send_email(subject, html_content)
            
        except Exception as e:
            logger.error(f"Błąd wysyłania emaila: {e}")
            return False
    
    def _send_email(self, subject: str, html_content: str) -> bool:
        """Wysyła email przez SMTP."""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Połącz z Gmail SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if Settings.USE_TLS:
                    server.starttls()
                
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            
            logger.info(f"✓ Email wysłany do {self.recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd wysyłania emaila: {e}")
            return False
    
    def _generate_html(self, events: List[Dict[str, Any]]) -> str:
        """Generuje HTML emaila."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .event {{ background: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; border-radius: 4px; }}
                .event-header {{ font-size: 1.2em; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
                .info-row {{ margin: 5px 0; }}
                .label {{ font-weight: bold; color: #7f8c8d; }}
                .value {{ color: #2c3e50; }}
                .stats {{ background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 4px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; font-size: 0.9em; }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚽ Forebet Scraper - Kwalifikowane Zdarzenia</h1>
                <p><strong>Data generacji:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Liczba zdarzeń:</strong> {len(events)}</p>
                <hr>
        """
        
        for i, event in enumerate(events, 1):
            ev = event.get('event', {})
            analysis = event.get('analysis', {})
            
            home_team = ev.get('home_team', 'N/A')
            away_team = ev.get('away_team', 'N/A')
            sport = ev.get('sport', 'N/A')
            league = ev.get('league', 'N/A')
            
            probs = ev.get('probabilities', {})
            home_prob = probs.get('home', 0)
            draw_prob = probs.get('draw', 0)
            away_prob = probs.get('away', 0)
            
            home_form = analysis.get('home_form', {})
            away_form = analysis.get('away_form', {})
            h2h = analysis.get('h2h', {})
            
            match_url = ev.get('match_url', '#')
            
            html += f"""
                <div class="event">
                    <div class="event-header">#{i} - {home_team} vs {away_team}</div>
                    
                    <div class="info-row">
                        <span class="label">Sport:</span> <span class="value">{sport.upper()}</span> |
                        <span class="label">Liga:</span> <span class="value">{league}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Prawdopodobieństwo:</span>
                        <span class="value">{home_prob}% - {draw_prob}% - {away_prob}%</span>
                    </div>
                    
                    <div class="stats">
                        <strong>Forma:</strong><br>
                        {home_team}: {home_form.get('record', 'N/A')} ({home_form.get('points', 0)} pkt)<br>
                        {away_team}: {away_form.get('record', 'N/A')} ({away_form.get('points', 0)} pkt)
                    </div>
            """
            
            if h2h.get('has_history'):
                html += f"""
                    <div class="stats">
                        <strong>Historia H2H:</strong><br>
                        Win rate gospodarzy: {h2h.get('home_win_rate', 0) * 100:.1f}%<br>
                        Mecze: {h2h.get('total_matches', 0)} (W:{h2h.get('home_wins', 0)} D:{h2h.get('draws', 0)} L:{h2h.get('away_wins', 0)})
                    </div>
                """
            
            html += f"""
                    <div class="info-row">
                        <a href="{match_url}" target="_blank">🔗 Zobacz szczegóły na Forebet</a>
                    </div>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p>Wygenerowane automatycznie przez Forebet Scraper</p>
                    <p>⚠️ Pamiętaj: To tylko analiza statystyczna, nie gwarancja wyniku!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


__all__ = ['EmailSender']

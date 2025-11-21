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
        """Generuje HTML emaila z grupowaniem po sportach."""
        # Grupuj wydarzenia po sporcie
        from collections import defaultdict
        events_by_sport = defaultdict(list)
        
        for event in events:
            sport = event.get('event', {}).get('sport', 'unknown')
            events_by_sport[sport].append(event)
        
        # Ikony sportów
        sport_icons = {
            'football': '⚽',
            'basketball': '🏀',
            'volleyball': '🏐',
            'hockey': '🏒',
            'handball': '🤾',
            'baseball': '⚾',
            'rugby': '🏉',
            'cricket': '🏏',
            'american-football': '🏈'
        }
        
        # Kolory dla sportów
        sport_colors = {
            'football': '#27ae60',
            'basketball': '#e67e22',
            'volleyball': '#9b59b6',
            'hockey': '#3498db',
            'handball': '#e74c3c',
            'baseball': '#16a085',
            'rugby': '#d35400',
            'cricket': '#8e44ad',
            'american-football': '#c0392b'
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; 
                    color: #2c3e50; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .container {{ 
                    max-width: 900px; 
                    margin: 0 auto; 
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{ 
                    margin: 0;
                    font-size: 2.2em;
                    font-weight: 700;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .header-info {{
                    margin-top: 15px;
                    font-size: 1.1em;
                    opacity: 0.95;
                }}
                .content {{
                    padding: 30px;
                }}
                .sport-section {{
                    margin-bottom: 40px;
                }}
                .sport-header {{
                    background: linear-gradient(135deg, var(--sport-color) 0%, var(--sport-color-dark) 100%);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    font-size: 1.5em;
                    font-weight: 600;
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }}
                .sport-icon {{
                    font-size: 1.3em;
                    margin-right: 12px;
                }}
                .event {{ 
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-left: 5px solid var(--sport-color);
                    padding: 20px; 
                    margin: 15px 0; 
                    border-radius: 8px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }}
                .event:hover {{
                    transform: translateX(5px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .event-header {{ 
                    font-size: 1.3em; 
                    font-weight: 700; 
                    color: #2c3e50; 
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                }}
                .vs-divider {{
                    margin: 0 10px;
                    color: var(--sport-color);
                    font-weight: 600;
                }}
                .info-row {{ 
                    margin: 8px 0;
                    font-size: 0.95em;
                }}
                .label {{ 
                    font-weight: 600; 
                    color: #7f8c8d;
                    display: inline-block;
                    min-width: 120px;
                }}
                .value {{ 
                    color: #34495e;
                    font-weight: 500;
                }}
                .probability {{
                    background: white;
                    padding: 12px;
                    margin: 12px 0;
                    border-radius: 6px;
                    font-size: 1.1em;
                    font-weight: 600;
                    text-align: center;
                    color: var(--sport-color);
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                }}
                .stats {{ 
                    background: rgba(255,255,255,0.9);
                    padding: 12px; 
                    margin: 12px 0; 
                    border-radius: 6px;
                    border: 1px solid #e0e0e0;
                }}
                .stats strong {{
                    color: var(--sport-color);
                    display: block;
                    margin-bottom: 6px;
                }}
                .form-row {{
                    margin: 5px 0;
                    padding: 4px 0;
                }}
                .footer {{ 
                    background: #34495e;
                    color: #ecf0f1;
                    padding: 25px 30px;
                    text-align: center;
                    font-size: 0.9em;
                }}
                .footer-warning {{
                    background: #e74c3c;
                    color: white;
                    padding: 10px;
                    border-radius: 6px;
                    margin-top: 15px;
                    font-weight: 600;
                }}
                a {{ 
                    color: var(--sport-color);
                    text-decoration: none;
                    font-weight: 600;
                    transition: opacity 0.2s;
                }}
                a:hover {{ 
                    opacity: 0.7;
                }}
                .link-button {{
                    display: inline-block;
                    background: var(--sport-color);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    margin-top: 10px;
                    text-decoration: none;
                    transition: transform 0.2s;
                }}
                .link-button:hover {{
                    transform: scale(1.05);
                    opacity: 1;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Forebet Scraper - Kwalifikowane Wydarzenia</h1>
                    <div class="header-info">
                        📅 Data: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | 
                        📊 Wydarzenia: {len(events)}
                    </div>
                </div>
                <div class="content">
        """
        
        # Generuj sekcje dla każdego sportu
        for sport, sport_events in sorted(events_by_sport.items()):
            sport_icon = sport_icons.get(sport, '🏆')
            sport_color = sport_colors.get(sport, '#3498db')
            sport_color_dark = self._darken_color(sport_color)
            sport_name = sport.replace('-', ' ').title()
            
            # Sporty z remisem (1/X/2) vs bez remisu (1/2)
            has_draw = sport in ['football', 'handball']
            
            html += f"""
                <div class="sport-section" style="--sport-color: {sport_color}; --sport-color-dark: {sport_color_dark};">
                    <div class="sport-header">
                        <span class="sport-icon">{sport_icon}</span>
                        <span>{sport_name} ({len(sport_events)})</span>
                    </div>
            """
            
            for i, event in enumerate(sport_events, 1):
                ev = event.get('event', {})
                analysis = event.get('analysis', {})
                
                home_team = ev.get('home_team', 'N/A')
                away_team = ev.get('away_team', 'N/A')
                league = ev.get('league', 'N/A')
                
                probs = ev.get('probabilities', {})
                home_prob = probs.get('home', 0)
                draw_prob = probs.get('draw', 0)
                away_prob = probs.get('away', 0)
                
                home_form = analysis.get('home_form', {})
                away_form = analysis.get('away_form', {})
                home_home = analysis.get('home_home_record', {})
                away_away = analysis.get('away_away_record', {})
                h2h = analysis.get('h2h', {})
                
                match_url = ev.get('match_url', '#')
                
                # Formatowanie prawdopodobieństwa w zależności od sportu
                if has_draw:
                    prob_text = f"1: {home_prob}% | X: {draw_prob}% | 2: {away_prob}%"
                else:
                    prob_text = f"1: {home_prob}% | 2: {away_prob}%"
                
                html += f"""
                    <div class="event">
                        <div class="event-header">
                            <span>{home_team}</span>
                            <span class="vs-divider">VS</span>
                            <span>{away_team}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">🏆 Liga:</span> 
                            <span class="value">{league}</span>
                        </div>
                        
                        <div class="probability">
                            {prob_text}
                        </div>
                        
                        <div class="stats">
                            <strong>📊 Forma Ogólna (ostatnie 6 meczów):</strong>
                            <div class="form-row">🏠 {home_team}: {home_form.get('display', 'N/A')}</div>
                            <div class="form-row">✈️ {away_team}: {away_form.get('display', 'N/A')}</div>
                        </div>
                        
                        <div class="stats">
                            <strong>🏟️ Forma Home/Away:</strong>
                            <div class="form-row">🏠 {home_team} u siebie: {home_home.get('display', 'N/A')}</div>
                            <div class="form-row">✈️ {away_team} na wyjeździe: {away_away.get('display', 'N/A')}</div>
                        </div>
                """
                
                if h2h.get('has_history'):
                    html += f"""
                        <div class="stats">
                            <strong>🤝 Historia Head-to-Head:</strong>
                            <div class="form-row">Win rate {home_team}: {h2h.get('home_win_rate', 0) * 100:.1f}%</div>
                            <div class="form-row">Mecze: {h2h.get('total_matches', 0)} (W:{h2h.get('home_wins', 0)} | D:{h2h.get('draws', 0)} | L:{h2h.get('away_wins', 0)})</div>
                        </div>
                    """
                
                html += f"""
                        <a href="{match_url}" target="_blank" class="link-button">
                            🔗 Zobacz szczegóły na Forebet
                        </a>
                    </div>
                """
            
            html += "</div>"  # Zamknij sport-section
        
        html += """
                </div>
                <div class="footer">
                    <p>🤖 Wygenerowane automatycznie przez Forebet Scraper</p>
                    <div class="footer-warning">
                        ⚠️ WAŻNE: To tylko analiza statystyczna oparta na danych historycznych.<br>
                        Nie stanowi gwarancji wyniku ani porady inwestycyjnej!
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Przyciemnia kolor hex."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


__all__ = ['EmailSender']

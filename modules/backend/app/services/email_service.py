"""
Email Service - Invio notifiche tramite Resend
"""
import resend
import structlog
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = structlog.get_logger()

# Dashboard URL (production)
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://sunpulse.giovannitommasini.it")


class EmailService:
    """Servizio per invio email tramite Resend"""
    
    def __init__(self):
        # Leggi direttamente dall'ambiente per evitare problemi di cache
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("EMAIL_FROM", "SunPulse <onboarding@resend.dev>")
        self.notification_email = os.getenv("NOTIFICATION_EMAIL")
        
        if self.api_key:
            resend.api_key = self.api_key
            logger.info("Email service initialized with Resend", notification_email=self.notification_email)
        else:
            logger.warning("Resend API key not configured - emails disabled")
    
    @property
    def is_configured(self) -> bool:
        """Verifica se il servizio email è configurato"""
        return bool(self.api_key)
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Invia una singola email"""
        if not self.is_configured:
            logger.warning("Email not sent - service not configured")
            return {"success": False, "error": "Email service not configured"}
        
        try:
            params = {
                "from": self.from_email,
                "to": [to],
                "subject": subject,
                "html": html,
            }
            if text:
                params["text"] = text
            
            result = resend.Emails.send(params)
            
            logger.info("Email sent successfully", to=to, subject=subject, id=result.get("id"))
            return {"success": True, "id": result.get("id")}
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e), to=to)
            return {"success": False, "error": str(e)}
    
    async def send_alarm_notification(
        self,
        alarm_type: str,
        alarm_message: str,
        device_name: str,
        severity: str = "warning",
        to_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Invia notifica per allarme"""
        recipient = to_email or self.notification_email
        if not recipient:
            return {"success": False, "error": "Notification email not configured"}
        
        severity_colors = {
            "critical": "#ff4d4f",
            "warning": "#faad14", 
            "info": "#1890ff"
        }
        color = severity_colors.get(severity, "#1890ff")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .device {{ background: #f0f2f5; padding: 10px 15px; border-radius: 4px; margin: 15px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Allarme {severity.upper()}</h1>
                </div>
                <div class="content">
                    <h2>{alarm_type}</h2>
                    <p>{alarm_message}</p>
                    <div class="device">
                        <strong>Dispositivo:</strong> {device_name}
                    </div>
                    <p><strong>Data:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                </div>
                <div class="footer">
                    <p>SunPulse - Monitoraggio Impianto Fotovoltaico</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"[SunPulse] Allarme {severity.upper()}: {alarm_type}"
        return await self.send_email(recipient, subject, html)
    
    async def send_daily_report(
        self,
        production_kwh: float,
        consumption_kwh: float,
        self_consumption_kwh: float,
        from_grid_kwh: float,
        to_grid_kwh: float,
        savings_eur: float,
        to_email: Optional[str] = None,
        system_name: str = "Il mio impianto"
    ) -> Dict[str, Any]:
        """Invia report giornaliero"""
        recipient = to_email or self.notification_email
        if not recipient:
            return {"success": False, "error": "Notification email not configured"}
        
        italy_tz = ZoneInfo("Europe/Rome")
        today = datetime.now(italy_tz)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #52c41a, #1890ff); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .stat-row {{ display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #eee; }}
                .stat-label {{ color: #666; }}
                .stat-value {{ font-weight: bold; font-size: 18px; }}
                .stat-value.green {{ color: #52c41a; }}
                .stat-value.orange {{ color: #faad14; }}
                .stat-value.blue {{ color: #1890ff; }}
                .savings {{ background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 8px; padding: 20px; margin-top: 20px; text-align: center; }}
                .savings-value {{ font-size: 32px; font-weight: bold; color: #52c41a; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>☀️ Report Giornaliero</h1>
                    <p>{system_name} - {today.strftime("%d/%m/%Y")}</p>
                </div>
                <div class="content">
                    <div class="stat-row">
                        <span class="stat-label">⚡ Produzione</span>
                        <span class="stat-value green">{production_kwh:.2f} kWh</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">🏠 Consumo</span>
                        <span class="stat-value orange">{consumption_kwh:.2f} kWh</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">☀️ Autoconsumo</span>
                        <span class="stat-value green">{self_consumption_kwh:.2f} kWh</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">🔌 Dalla Rete</span>
                        <span class="stat-value blue">{from_grid_kwh:.2f} kWh</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">⬆️ Immesso in Rete</span>
                        <span class="stat-value blue">{to_grid_kwh:.2f} kWh</span>
                    </div>
                    
                    <div class="savings">
                        <p>💰 Risparmio Oggi</p>
                        <div class="savings-value">€ {savings_eur:.2f}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>SunPulse - Monitoraggio Impianto Fotovoltaico</p>
                    <p><a href="{DASHBOARD_URL}">Vai alla Dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"[SunPulse] Report Giornaliero - {production_kwh:.1f} kWh prodotti"
        return await self.send_email(recipient, subject, html)
    
    async def send_weekly_report(
        self,
        total_production_kwh: float,
        total_consumption_kwh: float,
        total_self_consumption_kwh: float,
        total_from_grid_kwh: float,
        total_to_grid_kwh: float,
        total_savings_eur: float,
        daily_data: List[Dict[str, Any]],
        to_email: Optional[str] = None,
        system_name: str = "Il mio impianto"
    ) -> Dict[str, Any]:
        """Invia report settimanale con riepilogo 7 giorni"""
        recipient = to_email or self.notification_email
        if not recipient:
            return {"success": False, "error": "Notification email not configured"}
        
        italy_tz = ZoneInfo("Europe/Rome")
        today = datetime.now(italy_tz)
        week_start = today - timedelta(days=7)
        
        # Genera righe tabella per ogni giorno
        daily_rows = ""
        for day in daily_data:
            daily_rows += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{day.get('date', 'N/A')}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; color: #52c41a;">{day.get('production', 0):.1f}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; color: #faad14;">{day.get('consumption', 0):.1f}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; color: #1890ff;">{day.get('savings', 0):.2f}</td>
                </tr>
            """
        
        avg_production = total_production_kwh / 7 if total_production_kwh else 0
        avg_consumption = total_consumption_kwh / 7 if total_consumption_kwh else 0
        self_consumption_rate = (total_self_consumption_kwh / total_production_kwh * 100) if total_production_kwh > 0 else 0
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 650px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #1890ff, #722ed1); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .summary-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; }}
                .summary-card {{ background: #f9f9f9; padding: 15px; border-radius: 8px; text-align: center; }}
                .summary-value {{ font-size: 24px; font-weight: bold; }}
                .summary-label {{ color: #666; font-size: 12px; margin-top: 5px; }}
                .green {{ color: #52c41a; }}
                .orange {{ color: #faad14; }}
                .blue {{ color: #1890ff; }}
                .purple {{ color: #722ed1; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f0f2f5; padding: 12px; text-align: left; font-weight: 600; }}
                .savings-box {{ background: linear-gradient(135deg, #f6ffed, #e6fffb); border: 2px solid #52c41a; border-radius: 12px; padding: 25px; margin-top: 20px; text-align: center; }}
                .savings-value {{ font-size: 42px; font-weight: bold; color: #52c41a; }}
                .savings-label {{ color: #666; margin-top: 5px; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Report Settimanale</h1>
                    <p>{system_name}</p>
                    <p>{week_start.strftime("%d/%m")} - {today.strftime("%d/%m/%Y")}</p>
                </div>
                <div class="content">
                    <div class="summary-grid">
                        <div class="summary-card">
                            <div class="summary-value green">{total_production_kwh:.1f} kWh</div>
                            <div class="summary-label">⚡ Produzione Totale</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-value orange">{total_consumption_kwh:.1f} kWh</div>
                            <div class="summary-label">🏠 Consumo Totale</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-value blue">{self_consumption_rate:.0f}%</div>
                            <div class="summary-label">☀️ Autoconsumo</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-value purple">{avg_production:.1f} kWh</div>
                            <div class="summary-label">📈 Media Giornaliera</div>
                        </div>
                    </div>
                    
                    <h3>Dettaglio Giornaliero</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Produzione (kWh)</th>
                                <th>Consumo (kWh)</th>
                                <th>Risparmio (€)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {daily_rows}
                        </tbody>
                    </table>
                    
                    <div class="savings-box">
                        <div class="savings-label">💰 Risparmio Settimanale</div>
                        <div class="savings-value">€ {total_savings_eur:.2f}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>SunPulse - Monitoraggio Impianto Fotovoltaico</p>
                    <p><a href="{DASHBOARD_URL}">Vai alla Dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"[SunPulse] Report Settimanale - {total_production_kwh:.1f} kWh prodotti"
        return await self.send_email(recipient, subject, html)
    
    async def send_test_email(self, to: str) -> Dict[str, Any]:
        """Invia email di test"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                .header { background: #1890ff; color: white; padding: 30px; text-align: center; }
                .content { padding: 30px; text-align: center; }
                .success { color: #52c41a; font-size: 48px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>☀️ SunPulse</h1>
                </div>
                <div class="content">
                    <div class="success">✅</div>
                    <h2>Email di Test</h2>
                    <p>Congratulazioni! Il servizio email è configurato correttamente.</p>
                    <p>Riceverai notifiche per allarmi e report giornalieri.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to, "[SunPulse] Email di Test ✅", html)


# Singleton
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Ottieni istanza del servizio email"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

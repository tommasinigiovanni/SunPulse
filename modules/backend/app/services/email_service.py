"""
Email Service - Invio notifiche tramite Resend
"""
import resend
import structlog
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = structlog.get_logger()


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
        severity: str = "warning"
    ) -> Dict[str, Any]:
        """Invia notifica per allarme"""
        if not self.notification_email:
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
        return await self.send_email(self.notification_email, subject, html)
    
    async def send_daily_report(
        self,
        production_kwh: float,
        consumption_kwh: float,
        self_consumption_kwh: float,
        from_grid_kwh: float,
        to_grid_kwh: float,
        savings_eur: float
    ) -> Dict[str, Any]:
        """Invia report giornaliero"""
        if not self.notification_email:
            return {"success": False, "error": "Notification email not configured"}
        
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
                    <p>{datetime.now().strftime("%d/%m/%Y")}</p>
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
                    <p><a href="http://localhost:3000">Vai alla Dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"[SunPulse] Report Giornaliero - {production_kwh:.1f} kWh prodotti"
        return await self.send_email(self.notification_email, subject, html)
    
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

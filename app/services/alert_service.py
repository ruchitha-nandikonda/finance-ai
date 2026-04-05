from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from app.core.config import Settings
from app.models.schemas import BudgetStatus


class AlertService:
    """Sends email alerts when budgets are exceeded or nearly exceeded."""

    def __init__(self, config: Settings) -> None:
        self._config = config
        self._enabled = bool(config.smtp_user and config.smtp_password and config.alert_email)

    def check_and_alert(self, statuses: list[BudgetStatus]) -> list[str]:
        """Send alerts for over/warning budgets. Returns list of alert messages."""
        alerts: list[str] = []
        for s in statuses:
            if s.status == "over":
                msg = f"🔴 Over budget on {s.category}: spent ${s.spent:.2f} of ${s.monthly_limit:.2f} ({s.percentage:.0f}%)"
                alerts.append(msg)
            elif s.status == "warning":
                msg = f"🟡 Warning: {s.category} at {s.percentage:.0f}% of ${s.monthly_limit:.2f} budget"
                alerts.append(msg)

        if alerts and self._enabled:
            self._send_email(alerts)

        return alerts

    def _send_email(self, alerts: list[str]) -> None:
        body = "Budget Alerts:\n\n" + "\n".join(alerts)
        msg = MIMEText(body)
        msg["Subject"] = "💰 Finance Agent Budget Alert"
        msg["From"] = self._config.smtp_user
        msg["To"] = self._config.alert_email

        try:
            with smtplib.SMTP(self._config.smtp_host, self._config.smtp_port) as server:
                server.starttls()
                server.login(self._config.smtp_user, self._config.smtp_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send alert email: {e}")

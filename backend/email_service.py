"""Transactional mail via HTTPS APIs, with SMTP for compatible hosts."""
import base64
import logging
import smtplib
import ssl
from email.message import EmailMessage
from html import escape
from urllib.parse import urlencode
import requests
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    @property
    def configured(self):
        return settings.has_email

    @property
    def provider(self):
        if all([settings.GMAIL_CLIENT_ID, settings.GMAIL_CLIENT_SECRET, settings.GMAIL_REFRESH_TOKEN]):
            return "gmail"
        if settings.BREVO_API_KEY:
            return "brevo"
        if settings.SENDGRID_API_KEY:
            return "sendgrid"
        if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
            return "smtp"
        return None

    def send_email(self, to_email, subject, html_content, text_content=None):
        if not self.configured:
            return False
        message = EmailMessage()
        message["From"] = settings.FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(text_content or "Open this message in an HTML-capable email reader.")
        message.add_alternative(html_content, subtype="html")
        try:
            if self.provider == "gmail":
                token_response = requests.post("https://oauth2.googleapis.com/token", data={
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "refresh_token": settings.GMAIL_REFRESH_TOKEN,
                    "grant_type": "refresh_token",
                }, timeout=(10, 20))
                token_response.raise_for_status()
                token = token_response.json()["access_token"]
                response = requests.post("https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}, timeout=(10, 20))
                response.raise_for_status()
                return bool(response.json().get("id"))
            if self.provider == "brevo":
                payload = {"sender": {"email": settings.FROM_EMAIL, "name": "Kilele"},
                           "to": [{"email": to_email}], "subject": subject, "htmlContent": html_content}
                if text_content:
                    payload["textContent"] = text_content
                response = requests.post("https://api.brevo.com/v3/smtp/email",
                    headers={"api-key": settings.BREVO_API_KEY}, json=payload, timeout=(10, 20))
                response.raise_for_status()
                return bool(response.json().get("messageId"))
            if self.provider == "sendgrid":
                content = [{"type": "text/plain", "value": text_content}] if text_content else []
                content.append({"type": "text/html", "value": html_content})
                response = requests.post("https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"},
                    json={"from": {"email": settings.FROM_EMAIL}, "personalizations": [{"to": [{"email": to_email}]}],
                          "subject": subject, "content": content}, timeout=(10, 20))
                return response.status_code == 202
            transport = smtplib.SMTP_SSL if settings.SMTP_PORT == 465 else smtplib.SMTP
            options = {"context": ssl.create_default_context()} if settings.SMTP_PORT == 465 else {}
            with transport(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20, **options) as server:
                if settings.SMTP_PORT != 465:
                    server.starttls(context=ssl.create_default_context())
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                return not server.send_message(message)
        except (requests.RequestException, smtplib.SMTPException, OSError, ValueError, KeyError):
            # Provider responses can contain recipient addresses and OAuth credentials.
            logger.warning("Transactional mail delivery failed using %s", self.provider)
            return False

    def send_password_reset(self, to_email, reset_token, username):
        url = settings.FRONTEND_URL + "/Login?" + urlencode({"reset_token": reset_token})
        html = f'<p>Hi {escape(username)},</p><p><a href="{escape(url, quote=True)}">Reset your Kilele password</a></p><p>This link expires in 30 minutes and can be used once. Ignore it if you did not request a reset.</p>'
        return self.send_email(to_email, "Reset your Kilele password", html,
            f"Reset your Kilele password: {url}\nThis link expires in 30 minutes. Ignore it if you did not request it.")

    def send_welcome_email(self, to_email, username):
        return self.send_email(to_email, "Welcome to Kilele",
            f"<p>Welcome, {escape(username)}.</p><p>Your Kilele account is ready.</p>",
            f"Welcome, {username}. Your Kilele account is ready.")

    def send_achievement_notification(self, to_email, username, achievement_name):
        return self.send_email(to_email, "Kilele achievement unlocked",
            f"<p>Hi {escape(username)},</p><p>You earned {escape(achievement_name)}.</p>")
    
    def send_booking_confirmation(self, to_email, hike_name, reference):
        return self.send_email(to_email, "Kilele booking confirmed",
            f"<p>Your booking for {escape(hike_name)} is confirmed.</p><p>Reference: {escape(reference)}</p>",
            f"Your booking for {hike_name} is confirmed. Reference: {reference}")

    def send_booking_cancellation(self, to_email, hike_name, reference):
        text = f"Your booking for {hike_name} has been cancelled. Reference: {reference}. Contact kileleexplorers@gmail.com with questions."
        return self.send_email(to_email, "Kilele booking cancelled", f"<p>{escape(text)}</p>", text)

    def send_verification(self, to_email, token):
        url = settings.FRONTEND_URL + "/Login?" + urlencode({"verify_token": token})
        return self.send_email(to_email, "Verify your Kilele email", f'<p><a href="{escape(url, quote=True)}">Verify email address</a></p><p>This link expires in 30 minutes.</p>', f"Verify your email: {url}")


email_service = EmailService()

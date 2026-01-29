"""
Email service for Kilele
Supports SendGrid and SMTP
"""
import os
from typing import Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    from config import settings
except ImportError:
    settings = None

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.sendgrid_key = settings.SENDGRID_API_KEY if settings else None
        self.from_email = settings.FROM_EMAIL if settings else "noreply@kilele.app"
        self.smtp_configured = self._check_smtp()
        self.use_sendgrid = SENDGRID_AVAILABLE and self.sendgrid_key
    
    def _check_smtp(self) -> bool:
        """Check if SMTP is configured"""
        if not settings:
            return False
        return all([
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD
        ])
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email using SendGrid or SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if self.use_sendgrid:
            return self._send_via_sendgrid(to_email, subject, html_content, text_content)
        elif self.smtp_configured:
            return self._send_via_smtp(to_email, subject, html_content, text_content)
        else:
            print("⚠️ No email service configured")
            return False
    
    def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str]
    ) -> bool:
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if text_content:
                message.content = [
                    Content("text/plain", text_content),
                    Content("text/html", html_content)
                ]
            
            sg = SendGridAPIClient(self.sendgrid_key)
            response = sg.send(message)
            
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
            return False
    
    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str]
    ) -> bool:
        """Send email via SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.SMTP_FROM
            message["To"] = to_email
            
            # Add plain text and HTML parts
            if text_content:
                message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"❌ SMTP error: {e}")
            return False
    
    # Specific email templates
    
    def send_password_reset(self, to_email: str, reset_token: str, username: str) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.API_BASE_URL}/reset-password?token={reset_token}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1e3a5f;">🏔️ Kilele - Password Reset</h2>
                    <p>Hi {username},</p>
                    <p>You requested to reset your password. Click the button below to reset it:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background: #4a6fa5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                    </div>
                    <p>Or copy this link:</p>
                    <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all;">{reset_url}</p>
                    <p style="color: #666; font-size: 14px;">This link expires in 1 hour.</p>
                    <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">Kilele Hiking App - Explore Kenya's Trails</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        Kilele - Password Reset
        
        Hi {username},
        
        You requested to reset your password. Click the link below to reset it:
        
        {reset_url}
        
        This link expires in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Kilele Hiking App
        """
        
        return self.send_email(to_email, "Reset Your Kilele Password", html_content, text_content)
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email to new users"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1e3a5f;">🏔️ Welcome to Kilele!</h2>
                    <p>Hi {username},</p>
                    <p>Welcome to Kilele - Kenya's premier hiking trail app! We're excited to have you join our community of outdoor enthusiasts.</p>
                    <h3 style="color: #4a6fa5;">Get Started:</h3>
                    <ul>
                        <li>📍 Explore 7+ amazing Kenyan trails</li>
                        <li>🗺️ Track your hikes with GPS</li>
                        <li>⭐ Share reviews and photos</li>
                        <li>🏆 Earn achievements and badges</li>
                        <li>👥 Connect with fellow hikers</li>
                    </ul>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{settings.API_BASE_URL}" style="background: #4a6fa5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Start Exploring</a>
                    </div>
                    <p>Happy hiking! 🥾</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">Kilele Hiking App - Explore Kenya's Trails</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(to_email, "Welcome to Kilele! 🏔️", html_content)
    
    def send_achievement_notification(self, to_email: str, username: str, achievement_name: str) -> bool:
        """Send achievement unlock notification"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1e3a5f;">🏆 Achievement Unlocked!</h2>
                    <p>Hi {username},</p>
                    <p>Congratulations! You've unlocked a new achievement:</p>
                    <div style="background: linear-gradient(135deg, #4a6fa5 0%, #5b7ea8 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                        <h3 style="margin: 0; font-size: 24px;">✨ {achievement_name} ✨</h3>
                    </div>
                    <p>Keep up the great work and continue exploring Kenya's beautiful trails!</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">Kilele Hiking App - Explore Kenya's Trails</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(to_email, f"🏆 Achievement Unlocked: {achievement_name}", html_content)

# Global instance
email_service = EmailService()

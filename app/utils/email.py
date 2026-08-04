import os


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi.templating import Jinja2Templates
from app.core.config import get_email_settings, EmailSettings

templates = Jinja2Templates(directory="app/templates")

def send_password_reset_email(email: str, reset_url: str):
    """Renders the password reset HTML template and sends it via SMTP."""
    email_settings = get_email_settings()
    smtp_server = email_settings.SMTP_SERVER
    smtp_port = email_settings.SMTP_PORT
    smtp_user = email_settings.SMTP_USER
    smtp_password = email_settings.SMTP_PASSWORD
    mail_from = email_settings.MAIL_FROM

    # Render the HTML template using Jinja2
    template = templates.get_template("email_reset.html")
    html_content = template.render(reset_url=reset_url)

    # Build the email message container
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request — Vault"
    message["From"] = mail_from
    message["To"] = email

    # Attach the HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    #Connect to the SMTP server and send
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade connection to secure TLS
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(mail_from, email, message.as_string())
    except Exception as e:
        raise e
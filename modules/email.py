# modules/email.py - handles all email interactions as an object

import os
import smtplib
import logging


class Email:
    def __init__(self):
        self.email = os.environ.get("EMAIL_CLIENT_ADDRESS")
        self.password = os.environ.get("EMAIL_CLIENT_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.logger = logging.getLogger(
            f"discord.modules.{self.__class__.__name__.lower()}"
        )

    def send_email(self, recipient, subject, message):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.sendmail(
                    self.email, recipient, f"Subject: {subject}\n\n{message}"
                )
            self.logger.info(f"Email sent to {recipient}")
            return 0
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return -1

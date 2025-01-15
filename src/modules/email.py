# modules/email.py - handles all email interactions as an object

import os
import smtplib


class Email:
    def __init__(self):
        self.email = os.environ.get("EMAIL_CLIENT_ADDRESS")
        self.password = os.environ.get("EMAIL_CLIENT_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, recipient: str, subject: str, message: str):
        """
        Sends an email to the specified recipient with the given subject and message.

        Args:
            recipient (str): The recipient's email address.
            subject (str): The subject of the email.
            message (str): The message of the email.

        Returns:
            int: 0 if the email was sent successfully, -1 otherwise.
        """
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.sendmail(
                    self.email, recipient, f"Subject: {subject}\n\n{message}"
                )
            return 0
        except Exception as e:
            return -1

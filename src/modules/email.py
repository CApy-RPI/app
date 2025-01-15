# modules/email.py - handles all email interactions as an object

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email:
    def __init__(self):
        """Initialize the Email object with configuration from environment variables."""
        self.email = os.environ.get("EMAIL_CLIENT_ADDRESS")
        self.password = os.environ.get("EMAIL_CLIENT_PASSWORD")
        self.smtp_server = "smtp.gmail.com"  # Change to your SMTP server if not Gmail
        self.smtp_port = 587  # SMTP port for TLS

    def send_email(self, recipient: str, subject: str, message: str) -> int:
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
            # Create a multipart email message
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = recipient
            msg["Subject"] = subject

            # Attach the message body
            msg.attach(MIMEText(message, "plain"))

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(self.email, self.password)  # Log in to the server
                server.sendmail(
                    self.email, recipient, msg.as_string()
                )  # Send the email

            return 0  # Email sent successfully
        except Exception as e:
            print(f"Error sending email: {e}")  # Log the error for debugging
            return -1  # Email not sent

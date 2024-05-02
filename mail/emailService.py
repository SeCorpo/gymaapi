import logging
import os
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib import SMTPException
from dotenv import load_dotenv
import aiosmtplib

load_dotenv()
_email_connection = None  # Cached mail server connection object


async def create_email_connection():
    """
    Create and return an asynchronous mail server connection object.
    This function will attempt to create a connection using the SMTP credentials
    provided in environment variables and cache it globally.
    """
    global _email_connection
    if _email_connection is None:
        email_host = os.getenv("EMAIL_HOST")
        email_port = os.getenv("EMAIL_PORT")
        email_username = os.getenv("EMAIL_USERNAME")
        email_password = os.getenv("EMAIL_PASSWORD")
        use_tls = os.getenv("EMAIL_USE_TLS", True)

        try:
            smtp_client = aiosmtplib.SMTP(
                hostname=email_host, port=email_port, use_tls=use_tls
            )
            await smtp_client.connect()
            await smtp_client.login(email_username, email_password)
            _email_connection = smtp_client

        except SMTPException as e:
            logging.error(f"Failed to create mail connection: {e}")
            return None

    return _email_connection


async def send_email(recipient: str, subject: str, content: str, content_type="text/plain") -> bool:
    """ Sending a mail to recipient. Content_types can be 'text/plain' or 'text/html'. """
    try:
        smtp_client = await create_email_connection()
        if smtp_client is None:
            logging.error("Unable to send mail: Email connection is not available.")
            return False

        sender = os.getenv("EMAIL_USERNAME")

        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(content, content_type, 'utf-8'))

        await smtp_client.send_message(message)

        logging.info(f"Email successfully sent to {recipient}")
        return True

    except Exception as e:
        logging.error(f"Failed to send mail: {e}")
        return False

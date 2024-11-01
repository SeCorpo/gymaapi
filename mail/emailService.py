import logging
import os
import uuid
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib import SMTPException, SMTP
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
    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT"))
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
        logging.info("SMTP connection established and cached.")

    except SMTPException as e:
        logging.error(f"Failed to create mail connection: {e}")
        _email_connection = None

    return _email_connection


async def get_email_connection():
    """
    Get the email connection, creating it if necessary, and handle reconnection if needed.
    """
    global _email_connection

    if _email_connection is None or not _email_connection.is_connected:
        logging.info("Creating a new SMTP connection.")
        _email_connection = await create_email_connection()
    else:
        logging.info("Using cached SMTP connection.")

    return _email_connection


async def send_email(recipient: str, subject: str, content: str, content_type: str = "plain") -> bool:
    """ Sending a mail to recipient. Content_types can be 'plain' or 'html'. """
    smtp_client = None
    try:
        smtp_client = await get_email_connection()
        if smtp_client is None:
            logging.error("Unable to send mail: Email connection is not available.")
            return False

        sender_email = os.getenv("EMAIL_USERNAME")
        sender_name = os.getenv("EMAIL_NAME")
        sender = f"{sender_name} <{sender_email}>"

        domain = os.getenv("EMAIL_DOMAIN")

        message = MIMEMultipart('alternative')
        message['From'] = sender
        message['To'] = recipient
        message['Subject'] = Header(subject, 'utf-8')

        message_id = f"<{uuid.uuid4()}@{domain}>"
        message['Message-ID'] = message_id

        message.attach(MIMEText(content, content_type, 'utf-8'))

        await smtp_client.send_message(message)
        logging.info(f"Email successfully sent to {recipient}")
        return True

    except Exception as e:
        logging.error(f"Failed to send mail: {e}")
        return False


async def send_verification_email(verification_code: str, recipient: str) -> bool:
    """ Sending a verification code/ link to recipient, for email verification after registering. """
    logging.info(f"Sending verification code/ link to {recipient}")
    verification_url = os.getenv("WEBSITE_URL")

    subject = "Verify your Gyma account"
    link = f"{verification_url}/verify/{verification_code}"
    content = f"""
    <html>
        <body>
            <h1 style="color: #4e496f;">Verify Your Gyma Account</h1>
            <p>Thank you for registering at Gyma. 
                Please confirm your email address by clicking on the button below:</p>
            <table cellspacing="0" cellpadding="0"> <tr>
                <td align="center" width="200" height="40" bgcolor="#4e496f" style="display: block;">
                    <a href="{link}" style="font-size: 16px; font-family: Helvetica, Arial, sans-serif; color: #ffffff;
                    text-decoration: none; line-height:40px; width:100%; display:inline-block">
                    <span style="color: #ffffff;">Verify Email</span></a>
                </td>
            </tr> </table>
            <p>If you did not request this verification, please ignore this email.</p>
            <br>
            <p>If you cannot click the button, please copy and paste the URL below into your browser:</p>
            <p>{link}</p>
        </body>
    </html>
    """

    return await send_email(recipient, subject, content, "html")

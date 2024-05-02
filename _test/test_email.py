import unittest
from unittest.mock import patch, AsyncMock
import asyncio
from mail.emailService import create_email_connection, send_email


class MyTestCase(unittest.TestCase):
    def setUp(self):
        # Create a new event loop for each _test
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def run_async(self, coro):
        # Helper method to run the coroutine in the event loop
        return self.loop.run_until_complete(coro)

    @patch('aiosmtplib.SMTP', autospec=True)
    def test_create_email_connection(self, mock_smtp):
        # Set up the mock
        smtp_instance = mock_smtp.return_value
        smtp_instance.connect = AsyncMock(return_value=None)
        smtp_instance.starttls = AsyncMock(return_value=None)
        smtp_instance.login = AsyncMock(return_value=None)

        # Run the _test
        result = self.run_async(create_email_connection())

        # Assertions
        self.assertIsNotNone(result)
        smtp_instance.connect.assert_awaited_once()
        smtp_instance.starttls.assert_awaited_once()
        smtp_instance.login.assert_awaited_once()

    @patch('mail.emailService.create_email_connection', new_callable=AsyncMock)
    @patch('aiosmtplib.SMTP.send_message', new_callable=AsyncMock)
    def test_send_email(self, mock_send_message, mock_create_connection):
        # Set up the mock
        smtp_client = AsyncMock()
        mock_create_connection.return_value = smtp_client
        mock_send_message.return_value = asyncio.Future()
        mock_send_message.return_value.set_result(None)

        # Run the _test
        result = self.run_async(send_email("koldewijns99@gmail.com", "Test Subject", "Test content", "text/plain"))

        # Assertions
        self.assertTrue(result)
        mock_create_connection.assert_awaited_once()
        smtp_client.send_message.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()

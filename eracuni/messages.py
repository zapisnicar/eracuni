"""
Notifications module, send messages to console stdout, eMail and Telegram
"""


import smtplib
import ssl
import requests
import sys
from eracuni.data import Config


class Notifications:
    """
    Send notifications over console stdout, eMail and Telegram
    """
    def __init__(self, config: Config) -> None:
        self.config = config
        self.message_body = ''

    def add(self, text: str) -> None:
        """
        Add text to message body and report to stdout
        """
        self.message_body = self.message_body + text + '\n'
        # Report also to console stdout
        print(text)

    def send(self) -> None:
        """
        Send message
        """
        self.send_email()
        self.send_telegram()

    def send_email(self) -> None:
        """
        Send email, UTF-8 encoded text
        """
        if self.config.email_enabled and self.message_body != '':
            message = f"""\
From: {self.config.email_address}
To: {self.config.receiver_email}
Subject: Novi računi

{self.message_body}
"""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.config.smtp_server, self.config.ssl_port, context=context) as server:
                try:
                    server.login(self.config.email_address, self.config.email_password)
                    res = server.sendmail(
                        self.config.email_address, self.config.receiver_email, message.encode('utf8'))
                except:
                    print("Can't send email", file=sys.stderr)

    def send_telegram(self) -> None:
        """
        Send Telegram
        """
        if self.config.telegram_enabled and self.message_body != '':
            message = f'Novi računi:\n\n{self.message_body}'
            token = self.config.telegram_bot_token
            chat_id = self.config.telegram_chat_id
            url_req = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
            results = requests.get(url_req)
            if not results.json()['ok']:
                print("Can't send Telegram", file=sys.stderr)

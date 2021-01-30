"""
Notifications module, for email and telegram messages
"""


import smtplib
import ssl
import requests
import sys


class Notifications:
    """
    Send notifications over console, email and telegram
    """
    def __init__(self, config):
        self.config = config
        self.message_body = ''

    def add(self, text):
        """
        Add text to message body
        """
        self.message_body = self.message_body + text + '\n'
        # Report also to console
        print(text)

    def send(self):
        """
        Send message
        """
        self.send_email()
        self.send_telegram()

    def send_email(self):
        """
        Send email
        """
        if self.config.email_enabled and self.message_body != '':
            message = f'Novi računi:\n\n{self.message_body}'
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.config.smtp_server, self.config.ssl_port, context=context) as server:
                try:
                    server.login(self.config.email_address, self.config.email_password)
                    res = server.sendmail(self.config.email_address, self.config.receiver_email, message)
                except:
                    print("Can't send email", file=sys.stderr)

    def send_telegram(self):
        """
        Send telegram
        """
        if self.config.telegram_enabled and self.message_body != '':
            message = f'Novi računi:\n\n{self.message_body}'
            token = self.config.telegram_bot_token
            chat_id = self.config.telegram_chat_id
            url_req = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
            results = requests.get(url_req)
            if not results.json()['ok']:
                print("Can't send telegram", file=sys.stderr)

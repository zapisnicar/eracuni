"""
Notifications module, for email and telegram messages
"""


import smtplib
import ssl
import requests


class Notifications:
    def __init__(self, config):
        self.config = config
        self.email = Mail(config)
        self.telegram = Telegram(config)

    def add(self, text):
        self.email.add(text)
        self.telegram.add(text)

    def send(self):
        self.email.send()
        self.telegram.send()


class Mail:
    def __init__(self, config):
        self.enabled = config.email_enabled
        self.email_address = config.email_address
        self.email_password = config.email_password
        self.receiver_email = config.receiver_email
        self.smtp_server = config.smtp_server
        self.ssl_port = config.ssl_port
        self.message_body = ''

    def add(self, text):
        self.message_body = self.message_body + text + '\n'

    def send(self):
        if self.enabled and self.message_body != '':
            message = self.message_body
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.ssl_port, context=context) as server:
                try:
                    server.login(self.email_address, self.email_password)
                    res = server.sendmail(self.email_address, self.receiver_email, message)
                    print('email sent!')
                except:
                    print("could not login or send the mail.")


class Telegram:
    """
    Telegram messages
    """
    def __init__(self, config):
        self.enabled = config.telegram_enabled
        self.token = config.telegram_bot_token
        self.chat_id = config.telegram_chat_id
        self.message_body = ''

    def add(self, text):
        self.message_body = self.message_body + text + '\n'

    def send(self):
        if self.enabled and self.message_body != '':
            message = self.message_body
            url_req = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={message}'
            results = requests.get(url_req)
            # print(results.json())
            # print('Telegram message:\n' + self.message_body)

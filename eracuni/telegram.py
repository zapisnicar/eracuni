#!/usr/bin/env python3


import requests


class Telegram:
    """
    Telegram messages
    """
    def __init__(self, config):
        self.token = config.telegram_bot_token
        self.chat_id = config.telegram_chat_id
        self.enabled = config.send_telegram
        self.message = ''

    def add_text(self):
        pass

    def send(self):
        if self.enabled:
            url_req = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={self.message}'
            results = requests.get(url_req)
            # print(results.json())

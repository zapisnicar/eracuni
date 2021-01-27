#!/usr/bin/env python3


import requests


class Telegram:
    pass


def send_msg(text):
    token = '123456790:xxxxxxxxxxxxxxxxxxxxxx'
    chat_id = '-11111111111'
    url_req = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}'
    results = requests.get(url_req)
    print(results.json())

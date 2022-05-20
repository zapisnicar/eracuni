"""
Data module for configuration, data storage and file manipulation
"""


import os
import sys
import yaml
import platform
import shutil
from datetime import date
from pathlib import Path
from typing import List, Dict, Any


class Account:
    """
    Helper class for Config

    Account:
        user_id: string
        password: string
        alias: string
    """
    def __init__(self, user_id: str, password: str, alias: str) -> None:
        self.user_id = user_id
        self.password = password
        self.alias = alias


class Config:
    """
    Read configuration file, config.yaml:

    EDB_Domacinstva_Accounts:   List of EDB Domacinstva accounts
      - user_id:                user id
        password:               user password
        alias:                  alias, like home or garage
      - user_id:                other id
        password:               other password
        alias:
      - user_id:
        password:
        alias:

    EDB_Merna_Grupa_Accounts:   List of EDB Merna grupa accounts
      - user_id:                user id
        password:               user password
        alias:                  alias, like home2 or office
      - user_id:                other id
        password:               other password
        alias:
      - user_id:
        password:
        alias:

    InfoStan_Accounts:  List of InfoStan accounts
      - user_id:        user id
        password:       user password
        alias:          alias, like home or garage
      - user_id:        other id
        password:       other password
        alias:
      - user_id:
        password:
        alias:

    EDB_domacinstva_address:    EDB domacinstva Login page address
    EDB_merna_grupa_address:    EDB merna grupa Login page address
    InfoStan_address:           InfoStan Login page address
    headless:                   To start without GUI or not, True or False
    user_agent:                 Browser identifier string
    timeout:                    Selenium timeout

    email_enabled:      To send emails or not, True of False
    email_address:      Sender email address
    email_password:     Sender email password
    receiver_email:     Receiver email address
    smtp_server:        SMTP server
    ssl_port:           SMTP SSL port

    telegram_enabled:   To send Telegram messages or not, True of False
    telegram_bot_token: Telegram bot API token, in format: 1234567890:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    telegram_chat_id:   Telegram group Chat ID, in format: -11111111111

    Accounts with empty user_id are ignored
    If alias is empty, user_id will be used as alias
    There is no limit for how many accounts config file can have
    """
    def __init__(self) -> None:
        with open('config.yaml') as f:
            self.yaml_cfg: Dict[str, Any] = yaml.full_load(f)

        self.edb_domacinstva_accounts: List[Account] = []
        self.setup_edb_domacinstva_accounts()
        self.edb_domacinstva_url: str = self.yaml_cfg['EDB_domacinstva_address']

        self.edb_merna_grupa_accounts: List[Account] = []
        self.setup_edb_merna_grupa_accounts()
        self.edb_merna_grupa_url = self.yaml_cfg['EDB_merna_grupa_address']

        self.infostan_accounts: List[Account] = []
        self.setup_infostan_accounts()
        self.infostan_url: str = self.yaml_cfg['InfoStan_address']

        self.headless: bool = self.yaml_cfg['headless']
        self.user_agent: str = self.yaml_cfg['user_agent']
        self.timeout: float = self.yaml_cfg['timeout']

        self.email_enabled: bool = self.yaml_cfg['email_enabled']
        self.email_address: str = self.yaml_cfg['email_address']
        self.email_password: str = self.yaml_cfg['email_password']
        self.receiver_email: str = self.yaml_cfg['receiver_email']
        self.smtp_server: str = self.yaml_cfg['smtp_server']
        self.ssl_port: int = self.yaml_cfg['ssl_port']

        self.telegram_enabled: bool = self.yaml_cfg['telegram_enabled']
        self.telegram_bot_token: str = self.yaml_cfg['telegram_bot_token']
        self.telegram_chat_id: str = str(self.yaml_cfg['telegram_chat_id'])

    def setup_edb_domacinstva_accounts(self) -> None:
        # Get all EDB accounts
        for user in self.yaml_cfg['EDB_Domacinstva_Accounts']:
            user_id = str(user['user_id']).strip()
            if user_id != 'None':
                password = str(user['password'])
                alias = str(user['alias']).strip()
                if alias == 'None':
                    alias = user_id
                self.edb_domacinstva_accounts.append(Account(user_id, password, alias))

    def setup_edb_merna_grupa_accounts(self) -> None:
        # Get all EDB merna grupa accounts
        for user in self.yaml_cfg['EDB_Merna_Grupa_Accounts']:
            user_id = str(user['user_id']).strip()
            if user_id != 'None':
                password = str(user['password'])
                alias = str(user['alias']).strip()
                if alias == 'None':
                    alias = user_id
                self.edb_merna_grupa_accounts.append(Account(user_id, password, alias))

    def setup_infostan_accounts(self) -> None:
        # Get all InfoStan accounts
        for user in self.yaml_cfg['InfoStan_Accounts']:
            user_id = str(user['username']).strip()
            if user_id != 'None':
                password = str(user['password'])
                alias = str(user['alias']).strip()
                if alias == 'None':
                    alias = user_id
                self.infostan_accounts.append(Account(user_id, password, alias))

    @staticmethod
    def gecko_path() -> str:
        """
        Return path of geckodriver binary, OS dependent
        """
        my_system = platform.system()
        my_machine = platform.machine()
        if my_system == 'Linux' and my_machine == 'x86_64':
            # Linux PC
            exe_path = r'bin/linux64/geckodriver'
        elif my_system == 'Linux' and my_machine == 'armv7l':
            # Linux Raspberry Pi
            exe_path = r'bin/arm7hf/geckodriver'
        elif my_system == "Windows":
            # Windows
            exe_path = r'bin/win64/geckodriver.exe'
        elif my_system == "Darwin":
            # Mac
            # Notarization Workaround:
            # https://firefox-source-docs.mozilla.org/testing/geckodriver/Notarization.html
            exe_path = r'bin/macos/geckodriver'
        else:
            # No idea
            print(f"Unknown OS: {my_system}/{my_machine}", file=sys.stderr)
            sys.exit(1)

        return exe_path


class Storage:
    """
    Remember what was the last saved PDF bill, by last_saved id string
    Read and write var/storage_{file_name_infix}.yaml files, every user_id have separate one
    Use last_saved property as setter/getter
    """
    def __init__(self, file_name_infix: str) -> None:
        """
        Read last_saved from var/storage_{file_name_infix}.yaml
        If file does not exist, last_saved is "none"
        """
        self.file_name_infix = file_name_infix
        self.yaml_path = f'var/storage_{self.file_name_infix}.yaml'
        if os.path.isfile(self.yaml_path):
            with open(self.yaml_path, encoding='utf8') as fin:
                my_storage = yaml.full_load(fin)
            self.__last_saved = my_storage['last_saved'].strip()
        else:
            self.__last_saved = 'none'

    @property
    def last_saved(self) -> str:
        return self.__last_saved

    @last_saved.setter
    def last_saved(self, period: str) -> None:
        """
        Write var/{file_name_infix}.yaml
        """
        # TODO Fix UTF-8 characters in filenames
        self.__last_saved = period.strip()
        my_storage = {'last_saved': self.__last_saved}
        with open(self.yaml_path, 'w') as fout:
            # Dump my_storage with unicode characters to
            yaml.dump(my_storage, fout, encoding='utf8')

    def move_pdf(self) -> None:
        """
        Rename saved PDF file as {file_name_infix}_{YYYY-MM}_{original name}.pdf
        and move it to pdf subfolder
        """
        today = date.today().strftime('%Y-%m')
        for pdf_file in Path('var').glob('**/*.pdf'):
            new_path = f'pdf/{self.file_name_infix}_{today}_{pdf_file.stem}.pdf'
            shutil.move(str(pdf_file), new_path)

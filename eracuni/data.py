"""
Data module for configuration, storage and file manipulation
"""


import os
import sys
import yaml
import platform
import shutil
from datetime import date
from pathlib import Path


class Account:
    """
    Helper class for Config

    Account:
        user_id: string
        password: string
        alias: string
    """
    def __init__(self, user_id, password, alias):
        self.user_id = user_id
        self.password = password
        self.alias = alias


class Config:
    """
    Read configuration file, config.yaml:

    EDB_Accounts:       List of EDB accounts
      - user_id:        user id
        password:       user password
        alias:          alias, like home or garage
      - user_id:        other id
        password:       other password
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
    EDB_address:        EDB Login page address
    InfoStan_address:   InfoStan Login page address
    headless:           To start without GUI or not, True or False
    user_agent:         Browser identifier string

    Accounts with empty user_id are ignored
    If alias is empty, user_id will be used as alias
    There is no limit for how many accounts config file can have
    """
    def __init__(self):
        with open('config.yaml') as f:
            cfg = yaml.full_load(f)

        self.edb_accounts = []
        for user in cfg['EDB_Accounts']:
            user_id = str(user['user_id']).strip()
            if user_id != 'None':
                password = str(user['password'])
                alias = str(user['alias']).strip()
                if alias == 'None':
                    alias = user_id
                self.edb_accounts.append(Account(user_id, password, alias))

        self.infostan_accounts = []
        for user in cfg['InfoStan_Accounts']:
            user_id = str(user['username']).strip()
            if user_id != 'None':
                password = str(user['password'])
                alias = str(user['alias']).strip()
                if alias == 'None':
                    alias = user_id
                self.infostan_accounts.append(Account(user_id, password, alias))

        self.edb_url = cfg['EDB_address']
        self.infostan_url = cfg['InfoStan_address']
        self.headless = cfg['headless']
        self.user_agent = cfg['user_agent']
        self.timeout = cfg['timeout']
        self.gecko_path = gecko_path()


class Storage:
    """
    Remember what was the last saved PDF bill, by period id string
    Read and write data/{data_file_stem}.yaml files, every user_id have separate one
    Use period property as setter/getter
    """
    def __init__(self, data_file_stem):
        f"""
        Read last_period from data/{data_file_stem}.yaml
        If file does not exist, last_period is "none"
        """
        self.data_file_stem = data_file_stem
        self.yaml_path = f'data/{self.data_file_stem}.yaml'
        if os.path.isfile(self.yaml_path):
            with open(self.yaml_path) as fin:
                my_storage = yaml.full_load(fin)
            self.__period = my_storage['last_period'].strip()
        else:
            self.__period = 'none'

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, last_period):
        """
        Write data/{data_file_stem}.yaml
        """
        self.__period = last_period.strip()
        my_storage = {'last_period': self.__period}
        with open(self.yaml_path, 'w') as fout:
            yaml.dump(my_storage, fout)

    def move_pdf(self):
        """
        Rename saved PDF file as {data_file_stem}_{YYYY-MM}_{original name}.pdf
        and move it to pdf subfolder
        """
        today = date.today().strftime('%Y-%m')
        for pdf_file in Path('data').glob('**/*.pdf'):
            new_path = f'pdf/{self.data_file_stem}_{today}_{pdf_file.stem}.pdf'
            shutil.move(pdf_file, new_path)


def gecko_path():
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

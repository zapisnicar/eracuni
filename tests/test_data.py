

from eracuni.data import Account
import pytest


@pytest.fixture
def blatruc():
    print('blablablablabla')


def test_account(blatruc):
    x = Account('somename', 'somepassword', 'somealias')
    assert x.user_id == 'somename'
    assert x.password == 'somepassword'
    assert x.alias == 'somealias'

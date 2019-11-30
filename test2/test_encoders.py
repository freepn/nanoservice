import hashlib
import logging
from multiprocessing import Process

from nanoservice import Responder
from nanoservice import Requester
from nanoservice import encoder
from nanoservice import Authenticator

import pytest


def check(res, expected):
    if 'result' in res:
        chk_res = res['result']
    else:
        # there is no result for the ``none`` method so we fake it
        chk_res = None
    assert chk_res == expected


def start_service(addr, encoder, authenticator=None):
    """ Start a service with options """

    s = Responder(addr, encoder=encoder,
                  authenticator=authenticator, timeouts=(3000, 3000))
    s.register('none', lambda: None)
    s.register('divide', lambda x, y: x / y)
    s.register('upper', lambda dct: {k: v.upper() for k, v in dct.items()})
    s.start()


# ------------------
# Test Data

TESTS = [
    (('divide', [10, 2]), 5.0),
    (('none', []), None),
    (('upper', [{'a': 'a'}]), {'a': 'A'})
]

authenticators = [
    None,
    Authenticator('my-secret', hashlib.sha256)]

encoders = [
    encoder.JSONEncoder(),
    encoder.MsgPackEncoder(),
    encoder.PickleEncoder()]


def create_test_cases_encoding():
    """ Create test cases for encoding with different options """

    for test, expected in TESTS:
        for enc in encoders:
            for authenticator in authenticators:
                method, args = test
                yield authenticator, enc, method, args, expected


@pytest.mark.parametrize('auth,enc,method,args,expected', create_test_cases_encoding())
def test_encoding(auth, enc, method, args, expected):
    """ Test encoding using pytest decorator """
    address = 'ipc:///tmp/test-encoders.sock'

    # Start process
    proc = Process(
        target=start_service,
        args=(address, enc, auth))
    proc.start()

    # Create client
    client = Requester(
        address, encoder=enc,
        authenticator=auth, timeouts=(3000, 3000))

    # Test
    res = client.call(method, *args)
    client.socket.close()
    proc.terminate()
    check(res[0], expected)

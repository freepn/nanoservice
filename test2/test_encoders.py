import hashlib
import logging
from multiprocessing import Process

from nanoservice import Responder
from nanoservice import Requester
from nanoservice import encoder
from nanoservice import Authenticator


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


TESTS = [
    (('divide', [10, 2]), 5.0),
    (('none', []), None),
    (('upper', [{'a': 'a'}]), {'a': 'A'})
]


def test_encoding():
    """ Test encoding with defferent options """
    address = 'ipc:///tmp/test-encoders.sock'

    authenticators = [
        None,
        Authenticator('my-secret', hashlib.sha256)]

    encoders = [
        encoder.JSONEncoder(),
        encoder.MsgPackEncoder(),
        encoder.PickleEncoder()]

    for test, expected in TESTS:
        for enc in encoders:
            for authenticator in authenticators:
                method, args = test

                # Start process
                proc = Process(
                    target=start_service,
                    args=(address, enc, authenticator))
                proc.start()

                # Create client
                client = Requester(
                    address, encoder=enc,
                    authenticator=authenticator, timeouts=(3000, 3000))

                # Test
                res = client.call(method, *args)
                client.socket.close()
                proc.terminate()
                yield check, res[0], expected
                # self.assertEqual(expected, res)

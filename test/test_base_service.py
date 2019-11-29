import unittest
import uuid

from nanoservice import Responder
from nanoservice import Requester

from nanoservice import error
from nanoservice import crypto
from nanoservice.reqrep import RequestCtx


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        addr = 'inproc://test'
        self.client = Requester(addr)
        self.service = Responder(addr)
        self.service.register('divide', lambda x, y: x / y)
        self.service.register('echo', lambda x: x)

    def tearDown(self):
        self.client.socket.close()
        self.service.socket.close()


class TestResponder(BaseTestCase):

    def test_register_method(self):
        f = lambda x: x
        self.service.register(f, 'afun')

    def test_recv_method(self):
        sent = ['a', 'b', 'c']
        encoded = self.client.encoder.encode(sent)
        self.client.socket.send(encoded)
        got = self.service.receive()
        self.assertEqual(sent, got)

    def test_send_method(self):
        sent = ['a', 'b', 'c']
        self.test_recv_method()  # To send data to service
        self.service.send(sent)
        got = self.client.encoder.decode(self.client.socket.recv())
        self.assertEqual(sent, got)

    def test_exec_echo_success(self):
        ref = str(uuid.uuid4())
        ctx = RequestCtx(
            session=None,
            session_uuid=None,
            auth_token=None,
            ref=ref,
            version=3
        )
        #print(ctx)
        method, args = 'echo', ['hello world']
        res = self.service.execute(ctx, method, args)
        print(res['result'])
        self.assertTrue(res['result'] == 'hello world')

    def test_execute_method_w_success(self):
        ref = str(uuid.uuid4())
        ctx = RequestCtx(
            session=None,
            session_uuid=None,
            auth_token=None,
            ref=ref,
            version=1
        )
        #print(ctx)
        res = self.service.execute(ctx, 'divide', (6, 2))
        print(res['result'])
        expected = {'ref': ref, 'result': 3.0}
        #print(expected)
        self.assertEqual(res, expected)

    def test_execute_method_w_error(self):
        method = 'divide'
        args = (1, 0)
        ref = str(uuid.uuid4())
        res = {}
        ctx = RequestCtx(
            session=None,
            session_uuid=None,
            auth_token=None,
            ref=ref,
            version=2
        )
        #print(ctx)
        res = self.service.execute(ctx, method, args)
        print(res['error'])
        self.assertIsNotNone(res['error'])

    def test_encoder(self):
        data = {'name': 'Joe Doe'}
        encoded = self.service.encoder.encode(data)
        decoded = self.service.encoder.decode(encoded)
        self.assertEqual(data, decoded)

    def test_service_authenticate_simple(self):
        payload = 'no authentication set up. payload will be unchanged'
        got = self.service.verify(payload)
        self.assertEqual(got, payload)

    # Test error throwing

    def test_payload_decode_error(self):
        self.client.socket.send('"abc')
        self.assertRaises(error.DecodeError, self.service.receive)

    def test_payload_parse_error(self):
        for payload in [[1, 2], '', None]:
            self.assertRaises(
                error.RequestParseError, self.service.parse, payload)

    def test_payload_authenticate_error(self):
        payload = 'abc'
        auth = crypto.Authenticator('my secret')
        auth.unsigned = None  # Overwrite method to force error

        self.service.authenticator = auth
        self.client.authenticator = auth

        payload = self.client.encode(payload)
        payload = auth.signed(payload)
        self.client.socket.send(payload)
        self.assertRaises(
            error.AuthenticateError, self.service.receive)

    def test_payload_authenticator_invalid_signature(self):
        payload = 'abc'
        auth = crypto.Authenticator('my secret')
        self.service.authenticator = auth
        self.client.authenticator = auth

        payload = self.client.encode(payload)
        payload = auth.signed(payload)
        self.client.socket.send(b'123' + payload)
        self.assertRaises(
            error.AuthenticatorInvalidSignature, self.service.receive)


if __name__ == '__main__':
    unittest.main()

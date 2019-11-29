import unittest
from multiprocessing import Process

from nanoservice import Responder
from nanoservice import Requester
from nanoservice import encoder
from nanoservice import Authenticator


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.addr = 'ipc:///tmp/test-reqprep.sock'

    def tearDown(self):
        self.client.socket.close()

    def start_service(self, addr, authenticator=None):
        s = Responder(addr, authenticator=authenticator, timeouts=(3000, 3000))
        s.register('divide', lambda x, y: x / y)
        s.start()


class TestTCPProtocol(BaseTestCase):

    def make_req(self, *args):
        proc = Process(target=self.start_service, args=(self.addr,))
        proc.start()
        self.client = Requester(self.addr, timeouts=(3000, 3000))
        res = self.client.call('divide', *args)
        proc.terminate()
        return res

    def test_req_rep_w_success(self):
        res = self.make_req(6, 2)
        #print(res)
        self.assertEqual(3.0, res[0]['result'])

    def test_req_rep_w_error(self):
        res = self.make_req(6, 0)
        #print(res)
        self.assertIsNotNone(res[0]['error'])


class TestAuthentication(BaseTestCase):

    def make_req(self, *args):
        auth = Authenticator('my-secret')
        proc = Process(target=self.start_service,
                       args=(self.addr, auth))
        proc.start()
        self.client = Requester(
            self.addr, authenticator=auth, timeouts=(3000, 3000))
        res = self.client.call('divide', *args)
        proc.terminate()
        return res

    def test_req_rep_w_success(self):
        res = self.make_req(12, 2)
        #print(res)
        self.assertEqual(6.0, res[0]['result'])


class TestErrors(BaseTestCase):

    def make_req(self, *args):
        proc = Process(target=self.start_service, args=(self.addr,))
        proc.start()
        self.client = Requester(self.addr, timeouts=(3000, 3000))

        # Change encoder to force service to fail on encoding
        # since the service uses a MsgPack encoder
        self.client.encoder = encoder.JSONEncoder()

        # Build and send payload to service to trigger decoding
        payload = self.client.build_payload(None, 'divide', *args)
        self.client.send(payload)

        # Change back to msg pack encoder to read the service response
        self.client.encoder = encoder.MsgPackEncoder()

        out = self.client.receive()
        proc.terminate()
        return out

    def test_decode_error(self):
        # response now returns either error msg or result
        out = self.make_req(6, 2)
        #print(out)
        self.assertIsNotNone(out[0]['error'])


if __name__ == '__main__':
    unittest.main()

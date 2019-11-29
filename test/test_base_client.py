import unittest

from nanoservice import Responder
from nanoservice import Requester


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


class TestClient(BaseTestCase):

    def test_build_payload(self):
        payload = self.client.build_payload(None, None, 'echo', 'My Name')
        #print(payload[0]['met'])
        self.assertTrue(payload[0]['met'] == 'echo')
        self.assertTrue(payload[0]['arg'] == 'My Name')
        self.assertTrue(len(payload) == 1)

    def test_encoder(self):
        data = {'name': 'Joe Doe'}
        encoded = self.client.encode(data)
        decoded = self.client.decode(encoded)
        self.assertEqual(data, decoded)

    def test_call_wo_receive(self):
        # Requester side ops
        method, args = 'echo', 'hello world'
        payload = self.client.build_payload(None, None, method, args)
        self.client.socket.send(self.client.encode(payload))
        # Responder side ops
        response = self.service.receive()
        #print(response)
        method, args, ref = response[0]['met'], response[0]['arg'], response[0]['ref']
        self.assertEqual(method, 'echo')
        self.assertEqual(args, 'hello world')
        self.assertEqual(ref, payload[0]['ref'])

    def test_basic_socket_operation(self):
        msg = 'abc'
        self.client.socket.send(msg)
        res = self.service.socket.recv().decode('utf-8')
        self.assertEqual(msg, res)

    def test_timeout(self):
        c = Requester('inproc://timeout', timeouts=(1, 1))
        c.socket.send('hello')
        self.assertRaises(Exception, c.socket.recv)

if __name__ == '__main__':
    unittest.main()

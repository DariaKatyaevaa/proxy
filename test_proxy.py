import unittest
from web_proxy_server import ProxyServer
import proxy
from unittest import mock
import asyncio
import socket


class Proxy_test(unittest.TestCase):

    request_connect = b'CONNECT anytask.org:443 HTTP/1.1\r\n' \
                      b'Proxy-Connection: keep-alive\r\n' \
                      b'User-Agent: Mozilla/5.0 ' \
                      b'(Windows NT 10.0; Win64; x64) ' \
                      b'AppleWebKit/537.36 ' \
                      b'(KHTML, like Gecko)' \
                      b' Chrome/73.0.3683.103 Safari/537.36' \
                      b'\r\n\r\n'
    request_get = b'GET http//:doramy.club/ HTTP/1.1\r\n' \
                  b'Host: doramy.club' \
                  b'Proxy-Connection: keep-alive\r\n' \
                  b'User-Agent: Mozilla/5.0 ' \
                  b'(Windows NT 10.0; Win64; x64) ' \
                  b'AppleWebKit/537.36 ' \
                  b'(KHTML, like Gecko)' \
                  b' Chrome/73.0.3683.103 Safari/537.36' \
                  b'\r\n\r\n'
    parsed_dict = {
        "PORT": 443,
        "URL": "anytask.org",
        "DATA": request_connect,
        "Type": "CONNECT"
    }

    def test_request_parsing_connect(self):
        parsed = ProxyServer.parse_request(self.request_connect.decode())
        self.assertEqual(parsed["Type"], self.parsed_dict["Type"])

    def test_parsing_port(self):
        parsed = ProxyServer.parse_request(self.request_connect.decode())
        self.assertEqual(parsed["PORT"], self.parsed_dict["PORT"])

    def test_parsing_url(self):
        parsed = ProxyServer.parse_request(self.request_connect.decode())
        self.assertEqual(parsed["URL"], self.parsed_dict["URL"])

    def test_request_parsing_get(self):
        parsed = ProxyServer.parse_request(self.request_get.decode())
        self.assertEqual("GET", parsed["Type"])

    def test_get(self):
        mock_client = mock.Mock()
        atr = {"send.return_value": None,
               "close.return_value": None}
        mock_client.configure_mock(**atr)
        parsed = ProxyServer.parse_request(self.request_get.decode())
        ProxyServer.handle_get(mock_client, parsed)

    def test_connect(self):
        mock_client = mock.Mock()
        atr = {"send.return_value": None,
               "close.return_value": None}
        mock_client.configure_mock(**atr)
        proxy_ = ProxyServer()
        proxy_.handle_connect(mock_client, self.parsed_dict)

    def test_handle_request(self):
        mock_sock = mock.Mock()
        atr = {"settimeout.return_value": None,
               "recv.return_value": False,
               "close.return_value": None,
               "send.return_value": None}
        mock_sock.configure_mock(**atr)
        data = ProxyServer.receive(mock_sock)
        proxy_ = ProxyServer()
        asyncio.run(proxy_.handle_request(mock, self.request_connect))

    def test_proxy(self):
        mock_args = mock.MagicMock(port=8080)
        mock_empty = mock.MagicMock(port=False)
        test = list()
        test.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        test.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        asyncio.run(proxy.main(mock_empty, test=test))
        asyncio.run(proxy.main(mock_args, test=test))


if __name__ == '__main__':
    unittest.main()

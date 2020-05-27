import socket
import logging
from datetime import datetime


class ProxyServer:

    sockets = set()
    connections = {}

    @staticmethod
    def get_http_format_date():
        """Return a string representation of a date according to RFC 1123
            (HTTP/1.1)."""
        dt = datetime.today()
        weekday = ["Mon", "Tue", "Wed",
                   "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr",
                 "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % \
               (weekday, dt.day, month,
                dt.year, dt.hour, dt.minute, dt.second)

    @staticmethod
    def handle_get(client, parsed_request):
        """Handle GET request"""
        try:
            sock = socket.socket(socket.AF_INET,
                                 socket.SOCK_STREAM)
            sock.connect((parsed_request["URL"].encode(),
                          parsed_request["PORT"]))
            sock.send(parsed_request["DATA"])
            response = sock.recv(8192)
            sock.settimeout(20)
            while len(response):
                try:
                    client.send(response)
                    response = sock.recv(8192)
                except socket.timeout:
                    break
            client.send(b"\r\n\r\n")
            sock.close()
            client.close()
        except Exception as msg:
            logging.info("GET Error %s", str(msg))
            sock.close()
            client.close()

    def handle_connect(self, client, parsed_request):
        """Handle CONNECT HTTPS request"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
#            s = ssl.wrap_socket(s, "server.key", "server.crt")
            s.settimeout(10)
            self.connections[client] = s
            self.connections[s] = client
            self.connections[client].connect((parsed_request['URL'].encode(),
                                              parsed_request['PORT']))
            self.sockets.add(s)
            self.sockets.add(client)
            date = self.get_http_format_date().encode()
            client.send(b"HTTP/1.1 200 Connection established\r\n"
                        b"Date: " + date + b"\r\n"
                        b"Server: Apache/2.2.14 (Win64)\r\n"
                        b"\r\n")
        except Exception as msg:
            logging.info("CONNECT Error %s", str(msg))

    async def handle_request(self, sock, data):
        """Handle and check on correct request"""
        parsed_request = self.parse_request(data.decode())
        if parsed_request:
            if parsed_request['Type'] == 'GET':
                self.handle_get(sock, parsed_request)
            elif parsed_request['Type'] == 'CONNECT':
                self.handle_connect(sock, parsed_request)
            else:
                logging.info("Not correct request")
        else:
            sock.close()

    @staticmethod
    def receive(sock):
        """Read data from client"""
        sock.settimeout(3)
        data = b''
        try:
            while True:
                part = sock.recv(8192)
                if not part:
                    return data
                data += part
        finally:
            return data

    @staticmethod
    def parse_request(request):
        """Parse HTTP request"""
        logging.info(request + "\n\n")
        try:
            lines = request.splitlines()
            while lines[len(lines) - 1] == '':
                lines.remove('')
            first_line_tokens = lines[0].split()
            url = first_line_tokens[1]

            url_pos = url.find("://")
            if url_pos != -1:
                url = url[(url_pos + 3):]

            port_pos = url.find(":")
            path_pos = url.find("/")
            if path_pos == -1:
                path_pos = len(url)

            if port_pos == -1 or path_pos < port_pos:
                server_port = 80
                server_url = url[:path_pos]
            else:
                server_port = int(url[(port_pos + 1): path_pos])
                server_url = url[:port_pos]

            first_line_tokens[1] = url[path_pos:]
            lines[0] = ' '.join(first_line_tokens)
            client_data = "\r\n".join(lines) + '\r\n\r\n'

            parsed_request = {
                "PORT": server_port,
                "URL": server_url,
                "DATA": client_data.encode(),
                "Type": first_line_tokens[0]
            }
            logging.info(str(parsed_request))
            return parsed_request
        except Exception as msg:
            logging.info("Parsing error: %s", str(msg))

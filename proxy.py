import socket
import sys
from web_proxy_server import ProxyServer
import logging
import select
import argparse
import asyncio


async def main(args, test=False):
    log = logging.basicConfig(filename="proxy.log",
                              level=logging.INFO)
    proxy = ProxyServer()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if args.port:
            s.bind(('127.0.0.1', args.port))
            print("Working on localhost:", args.port)
        else:
            s.bind(('127.0.0.1', 8080))
            print("Working on localhost:8080 ...")
        s.listen(200)
        logging.info("RUN\n")
        proxy.sockets.add(s)
    except Exception as msg:
        logging.info(str(msg))
        sys.exit()

    while True:
        try:
            if not test:
                inputs, _, _ = select.select(proxy.sockets, [], [])
            else:
                inputs = test
            for sock in inputs:
                if sock == s:
                    client, address = sock.accept()
                    data = proxy.receive(client)
                    await proxy.handle_request(client, data)
                else:
                    try:
                        data = proxy.receive(sock)
                        if data:
                            proxy.connections[sock].send(data)
                    except Exception as msg:
                        logging.info(str(msg))
            if test:
                s.close()
                break
        except Exception as msg:
            client.close()
            logging.info(str(msg))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Proxy",
                                     description="Proxy-server for "
                                                 "GET and CONNECT request")
    parser.add_argument("-port", type=int,
                        help="Input port for server.")
    args = parser.parse_args()
    asyncio.run(main(args))

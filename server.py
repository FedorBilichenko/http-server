import socket
import os

from src.config import Config


def main():
    config = Config()
    print("Starting server on port {}, document root: {}".format(config.port, config.document_root))

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind(("", config.port))
    sock.listen(1)


if __name__ == '__main__':
    main()



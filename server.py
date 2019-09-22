import socket
import os

from src.config import Config
from src.selector import Selector
from src.handlers import ListenHandler


def main():
    config = Config()
    print("Starting server on port {}, document root: {}".format(config.port, config.document_root))

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind(("", config.port))
    sock.listen(1)

    selector = Selector(sock)

    for i in range(config.cpu_count - 1):
        pid = os.fork()
        if pid == 0:
            break

    selector.register(sock.fileno(), ListenHandler(sock))

    selector.start()


if __name__ == '__main__':
    main()



import socket
import os
import sys
import select
from src.config import Config


def main():
    config = Config().get_dict()

    print("Port {}, document root: {}".format(config.get('port'), config.get('document_root')))

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind((config.get('host'), config.get('port')))
    sock.listen(config.get('queue_size'))



if __name__ == '__main__':
    main()



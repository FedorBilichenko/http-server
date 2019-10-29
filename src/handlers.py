import os
from .http import HttpHandler

FILE_BLOCK_SIZE = 1024
READ_CHUNK_SIZE = 1024


class Handler:
    def __init__(self):
        self.ready_to_read = True
        self.ready_to_write = False
        self.ready = False
        self.has_file = False

    def read(self):
        pass


class FileHandler(Handler):
    def __init__(self, file, connection):
        super().__init__()
        self.file = file
        self.conn = connection

    def read(self):
        buffer = os.read(self.file, FILE_BLOCK_SIZE)
        if buffer:
            return buffer
        else:
            self.ready_to_read = False
            self.ready = True
            return b''


class ConnectionHandler(Handler):
    def __init__(self, connection, document_root='/var/www/html'):
        super().__init__()
        self.connection = connection
        self.data = b''
        self.out_data = b''
        self.httpHandler = HttpHandler()
        self.file_end = False
        self.document_root = document_root

    def read_data(self):
        try:
            chunk = self.connection.recv(READ_CHUNK_SIZE)
            self.data += chunk
            if len(chunk) < READ_CHUNK_SIZE:
                self.ready_to_read = False
                self.__handle()
        except:
            self.ready = True

    def __handle(self):
        self.out_data = self.httpHandler.handle_request(self.data, self.document_root)
        self.ready_to_write = True

        if self.httpHandler.file is not None:
            self.has_file = True
            self.file = self.httpHandler.file
        else:
            self.file_end = True

    def write_data(self):
        try:
            sent = self.connection.send(self.out_data)
            if self.file_end and len(self.out_data) == sent:
                self.ready = True
                self.ready_to_write = False
            self.out_data = self.out_data[sent:]
        except (BrokenPipeError, ConnectionResetError):
            self.ready = True
            self.ready_to_write = False

    def add_data(self, data):
        self.out_data += data


class ListenHandler(Handler):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

import os
import select
from .handlers import FileHandler, ConnectionHandler, ListenHandler


class Selector:
    def __init__(self, sock):
        self.sock = sock
        self.handlers_map = {}

    def register(self, fileno, handler):
        self.handlers_map[fileno] = handler

    def start(self):
        while True:
            ready_to_read = []
            ready_to_write = []
            for handler in list(self.handlers_map):
                if self.handlers_map[handler].ready_to_read:
                    ready_to_read.append(handler)
                if self.handlers_map[handler].ready_to_write:
                    ready_to_write.append(handler)
                if self.handlers_map[handler].has_file:
                    self.register(self.handlers_map[handler].file,
                                  FileHandler(self.handlers_map[handler].file, handler))
                    self.handlers_map[handler].has_file = False
                    ready_to_read.append(self.handlers_map[handler].file)

                if self.handlers_map[handler].ready:
                    if type(self.handlers_map[handler]) == FileHandler:
                        if self.handlers_map[handler].conn in self.handlers_map:
                            self.handlers_map[self.handlers_map[handler].conn].file_end = True
                        os.close(handler)
                    if type(self.handlers_map[handler]) == ConnectionHandler:
                        self.handlers_map[handler].connection.close()
                    del self.handlers_map[handler]

            try:
                r, w, e = select.select(ready_to_read, ready_to_write, self.handlers_map)
            except OSError:
                r, w, e = [], [], []

            for readable in r:
                if readable not in self.handlers_map:
                    continue
                if type(self.handlers_map[readable]) == ListenHandler:
                    try:
                        conn, addr = self.sock.accept()
                        conn.setblocking(0)
                        self.register(conn.fileno(), ConnectionHandler(conn))
                    except:
                        pass

                if type(self.handlers_map[readable]) == ConnectionHandler:
                    self.handlers_map[readable].read_data()

                if type(self.handlers_map[readable]) == FileHandler:
                    if self.handlers_map[readable].conn in self.handlers_map:
                        self.handlers_map[self.handlers_map[readable].conn].add_data(self.handlers_map[readable].read())
                    else:
                        self.handlers_map[readable].ready = True

            for writable in w:
                if writable not in self.handlers_map:
                    continue
                if type(self.handlers_map[writable]) == ConnectionHandler:
                    self.handlers_map[writable].write_data()

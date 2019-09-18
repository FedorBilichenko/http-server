from pathlib import Path

DEFAULT_CPU_COUNT = 4
DEFAULT_DOCUMENT_ROOT = '/var/www/html'
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080
DEFAULT_QUEUE_SIZE = 1

DEFAULT_PATH = './default.conf'


class Config:
    __slots__ = ['document_root', 'host', 'port', 'cpu_count', 'queue_size', 'path']

    def __init__(self, path=DEFAULT_PATH):
        self.document_root = DEFAULT_DOCUMENT_ROOT
        self.host = DEFAULT_HOST
        self.port = DEFAULT_PORT
        self.cpu_count = DEFAULT_CPU_COUNT
        self.queue_size = DEFAULT_QUEUE_SIZE
        self.path = path

        self._read()

    def _parse(self):
        with open(self.path, 'r') as file:
            for line in file.read().splitlines():
                key, value = line.split(' ')
                if hasattr(self, key):
                    if key in ['cpu_count', 'port', 'queue_size']:
                        setattr(self, key, int(value, 10))
                    else:
                        setattr(self, key, value)

    def _read(self):
        if not Path(self.path).is_file():
            self.path = DEFAULT_PATH

        self._parse()

    def get_dict(self):
        return {
            'document_root': self.document_root,
            'host': self.host,
            'port': self.port,
            'cpu_count': self.cpu_count,
            'queue_size': self.queue_size
        }

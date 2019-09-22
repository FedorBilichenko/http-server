from pathlib import Path

DEFAULT_CPU_LIMIT = 4
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '80'
DEFAULT_DOCUMENT_ROOT = '/var/www/html'
DEFAULT_QUEUE_SIZE = 1

DEFAULT_PATH = './default.conf'


class Config:
    __slots__ = [
        'cpu_count',
        'host',
        'port',
        'document_root',
        'queue_size',
        'path'
    ]

    def __init__(self):
        self.cpu_count = DEFAULT_CPU_LIMIT
        self.host = DEFAULT_HOST
        self.port = DEFAULT_PORT
        self.document_root = DEFAULT_DOCUMENT_ROOT
        self.queue_size = DEFAULT_QUEUE_SIZE
        self.path = DEFAULT_PATH

        self._read()

    def _read(self):
        if Path('/etc/httpd.conf').is_file():
            self.path = '/etc/httpd.conf'
        self._parse()

    def _parse(self):
        with open(self.path, 'r') as file:
            for line in file.read().splitlines():
                key, value = line.split(' ')
                if hasattr(self, key):
                    if key in ['cpu_count', 'port', 'queue_size']:
                        parsed = int(value, 10)
                        setattr(self, key, parsed)
                    else:
                        setattr(self, key, value)

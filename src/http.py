import datetime
from enum import Enum

ALLOWED_METHODS = ['GET', 'HEAD']


class ResponseCode(Enum):
    OK = '200 OK'
    NOT_FOUND = '404 Not Found'
    NOT_ALLOWED = '405 Method Not Allowed'
    FORBIDDEN = '403 Forbidden'


class HttpRequester:
    __slots__ = ['_data', '_method', '_uri', '_version', '_headers', '_body', '_error']

    def __init__(self, raw_data):
        self._error = False
        self._data = raw_data.decode('UTF-8')
        self._method = None
        self._uri = ''
        self._version = None
        self._headers = {}
        self._body = ''

    def get_method(self):
        return self._method

    def get_uri(self):
        return self._uri

    def get_error(self):
        return self._error

    def _parse(self):
        try:
            [request_line, content] = self._data.split('\r\n', maxsplit=1)
            [headers, self._body] = content.split('\r\n\r\n')

            [self._method, self._uri, self._version] = request_line.split(' ')

            if len(self._uri) == 0:
                self._uri = '/'

            for header in headers.split('\r\n'):
                [key, value] = header.split(': ')
                self._headers[key] = value

            if self._method not in ALLOWED_METHODS:
                self._error = True
            else:
                self._error = False
        except Exception:
            pass


class HttpResponser:
    def __init__(self, code, protocol, content_type=None, content_length=0, data=b''):
        self.code = code
        self.protocol = protocol
        self.data = data
        self.content_type = content_type
        self.content_length = content_length
        self.date = datetime.datetime.now()

    def _success(self):
        return 'HTTP/{} {}\r\n' \
               'Content-Type: {}\r\n' \
               'Content-Length: {}\r\n'\
               'Date: {}\r\n' \
               'Server: Server\r\n\r\n'.format(self.protocol,
                                               self.code.value,
                                               self.content_type,
                                               self.content_length,
                                               self.date)

    def _not_found(self):
        return 'HTTP/{} {}\r\n' \
               'Server: Server'.format(self.protocol, self.code.value)

    def build(self):
        if self.code == ResponseCode.OK:
            return self._success().encode() + self.data
        if self.code == ResponseCode.NOT_FOUND \
                or self.code == ResponseCode.NOT_ALLOWED \
                or self.code == ResponseCode.FORBIDDEN:
            return self._not_found().encode()


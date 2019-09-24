import urllib.parse
import datetime
import os
import fcntl
from enum import Enum


class ContentTypes(Enum):
    html = 'text/html'
    css = 'text/css'
    js = 'text/javascript'
    jpg = 'image/jpeg'
    jpeg = 'image/jpeg'
    png = 'image/png'
    swf = 'application/x-shockwave-flash'
    gif = 'image/gif'
    txt = 'text/txt'


class ResponseCode(Enum):
    OK = '200 OK'
    NOT_FOUND = '404 Not Found'
    NOT_ALLOWED = '405 Method Not Allowed'
    FORBIDDEN = '403 Forbidden'


ALLOWED_REQUEST_METHODS = ['GET', 'HEAD']


DEFAULT_METHOD = 'GET'
DEFAULT_PROTOCOL = '1.1'
DEFAULT_URL = '/'
DEFAULT_HEADERS = {}
DEFAULT_BODY = None
DEFAULT_CONTENT_TYPE = ''
DEFAULT_CONTENT_LENGTH = 0

DEFAULT_FILE = 'index.html'


class HTTPRequester:
    def __init__(self, data):
        self.is_method_allowed = False
        self.data = data.decode('UTF-8')
        self.method = DEFAULT_METHOD
        self.protocol = DEFAULT_PROTOCOL
        self.url = DEFAULT_URL
        self.headers = DEFAULT_HEADERS
        self.body = DEFAULT_BODY

        self._parse()

    def _parse(self):
        [request_line, content] = self.data.split('\r\n', maxsplit=1)
        [headers, self.body] = content.split('\r\n\r\n')

        [self.method, self.url, self.protocol] = request_line.split(' ')

        if self.url == '':
            self.url = '/'

        self.url, *_ = self.url.split('?')
        self.url = urllib.parse.unquote(self.url)

        if self.method in ALLOWED_REQUEST_METHODS:
            self.is_method_allowed = True

        self.protocol = self.protocol.replace('HTTP/', '')

        for header in headers.split('\r\n'):
            [key, value] = header.split(': ')
            self.headers[key] = value


class HTTPResponser:
    def __init__(self, code, protocol, content_type=None, content_length=0):
        self.code = code
        self.protocol = protocol
        self.content_type = content_type
        self.content_length = content_length
        self.date = datetime.datetime.now()

    def _build_success(self):
        return 'HTTP/{} {}\r\n' \
               'Content-Type: {}\r\n' \
               'Content-Length: {}\r\n'\
               'Date: {}\r\n' \
               'Connection: close\r\n' \
               'Server: Server\r\n\r\n'.format(self.protocol,
                                               self.code.value,
                                               self.content_type,
                                               self.content_length,
                                               self.date)

    def _build_error(self):
        return 'HTTP/{} {}\r\n' \
               'Server: Server\r\n\r\n'.format(self.protocol, self.code.value)

    def build(self):
        if self.code != ResponseCode.OK:
            return self._build_error().encode()
        return self._build_success().encode()


class HttpHandler:
    def __init__(self):
        self.protocol = DEFAULT_PROTOCOL
        self.content_type = DEFAULT_CONTENT_TYPE
        self.content_length = DEFAULT_CONTENT_LENGTH
        self.response = None
        self.file = None

    def handle_request(self, data, document_root):
        request = HTTPRequester(data)

        if not request.is_method_allowed:
            print('HERE')
            return HTTPResponser(ResponseCode.NOT_ALLOWED, request.protocol).build()

        self.protocol = request.protocol
        if request.url[-1:] == '/':
            file_url = request.url[1:] + DEFAULT_FILE
        else:
            file_url = request.url[1:]
        print('file_url', file_url)
        if file_url.find('../') >= 0:
            self.response = HTTPResponser(ResponseCode.FORBIDDEN, request.protocol)
        else:
            try:
                self.file = os.open(os.path.join(document_root, file_url), os.O_RDONLY | os.O_NONBLOCK)
                # flag = fcntl.fcntl(self.file, fcntl.F_GETFL)
                # fcntl.fcntl(self.file, fcntl.F_SETFL, flag | os.O_NONBLOCK)
            except (FileNotFoundError, IsADirectoryError):
                print('kek1')
                if (request.url[-1:]) == '/':
                    return HTTPResponser(ResponseCode.FORBIDDEN, request.protocol).build()
                else:
                    return HTTPResponser(ResponseCode.NOT_FOUND, request.protocol).build()
            except OSError:
                print('kek2')
                return HTTPResponser(ResponseCode.NOT_FOUND, request.protocol).build()
            try:
                self.content_type = ContentTypes[file_url.split('.')[-1]].value
            except KeyError:
                print('kek3')
                self.content_type = DEFAULT_CONTENT_TYPE

            self.content_length = os.path.getsize(os.path.join(document_root, file_url))
            self.response = HTTPResponser(ResponseCode.OK, request.protocol, self.content_type, self.content_length)

            if request.method == 'HEAD':
                self.file = None
        print(self.response.build())
        return self.response.build()

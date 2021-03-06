# -*- coding: utf-8 -*-
"""
Server
------

HTTP/HTTPS python server which exposes behaviour through the :class:`Server`
class.

.. code::

    >>> server = start_server()
    >>> server.data['response_content'] = b'this is response body text'
    >>> response = requests.get(server.url('/test'))
    >>> response.content
    'this is response body text'
"""
import os
import ssl
import time
import logging
import contextlib
from threading import Thread, RLock

from ._compat import (iteritems, ThreadingMixIn, HTTPServer,
                      BaseHTTPRequestHandler)


def here(path):
    return os.path.abspath(os.path.realpath(
        os.path.join(os.path.dirname(__file__), path)))


DEFAULT_HOST = '127.0.0.1'               # loopback
DEFAULT_PORT = 0                         # random port
DEFAULT_CERTFILE = here('./server.pem')  # cert + private key

lock = RLock()


log = logging.getLogger('httptestserver.http')


def start_server(host=None, port=None):
    """Create a started HTTP server listening in *host*:*port*

    :param host: *(default: 127.0.0.1)* Host for the server to listen.
    :param port: *(default: random)* Port of the server to listen (should not be in use).
    :returns: A created and started :class:`Server`
    """
    return Server.start_server(host or DEFAULT_HOST, port or DEFAULT_PORT)


def start_ssl_server(host=None, port=None, certfile=None, keyfile=None):
    """Create a started HTTPS server listening in *host*:*port*

    It configures server certificate using *certfile* and *keyfile*.

    :param host: *(default: 127.0.0.1)* Host for the server to listen.
    :param port: *(default: random)* Port of the server to listen (should not be in use).
    :param certfile: *(default: packaged .pem)* Path to certificate file as
     accepted by :class:`HTTPServer`.
    :param keyfile: *(default: None)* Path to private key file as accepted by
     :class:`HTTPServer`. Default comes bundled with *certfile*.
    :returns: A created and started :class:`Server`
    """
    return Server.start_ssl_server(host or DEFAULT_HOST, port or DEFAULT_PORT,
                                   certfile or DEFAULT_CERTFILE, keyfile)


class Handler(BaseHTTPRequestHandler):
    """Handles all requests and collects server data

    Handles all the requests on the :meth:`handle_request` method which is
    also responsible for building a response.

    The :attr:`Server.data` dictionary is updated on at the begining of each
    request with the current server state. See :class:`BaseHTTPRequestHandler`
    documentation for the full list of server attributes available.

    The default handler behaviour can be controlled through
    :attr:`Server.data`.
    """
    def handle_request(self):
        """Handles server request/response"""
        log.info('Processing %s request', self.command)

        # Read and process a http request
        # Create and send a http response
        self.server.process_hook('before_request')
        self.update_state()        # Save server current state
        self.read_content()        # Read request body
        self.save_history()        # Save current state in history

        self.server.process_hook('before_response', self.server.data)
        response = self.process_request()  # Process received request
        self.server.process_hook('after_response', self.server.data, response)

        self.send_http_response(response)  # send status, headers and content
        self.server.process_hook('after_request', self.server.data, response)
        self.finish_request()  # Optionally reset server state

    def read_content(self):
        # Read request body (if any)
        if self.command in ('POST', 'PUT', 'PATCH'):
            content_length = self.headers['Content-Length']
            log.info('Content-Length: %s', content_length)
            self.server.data['body'] = self.rfile.read(int(content_length))

    def process_request(self):
        # Simulate timeouts
        timeout = self.server.data.get('response_timeout')
        if timeout is not None:
            log.info('Server sleeping for: %d s', timeout)
            time.sleep(timeout)

        return self.create_response()

    def create_response(self):
        return HttpResponse(
            status=self.server.data.get('response_status', 200),
            headers=self.server.data.get('response_headers', ()),
            content=self.server.data.get('response_content', None),
        )

    def send_http_response(self, response):
        self.send_status(response.status)
        self.send_headers(response.headers)
        self.send_content(response.content)

    def send_status(self, status):
        log.info('Server returning status code %d', status)
        self.send_response(status)

    def send_headers(self, headers):
        for field, content in iteritems(headers):
            log.info('Server setting response header %s: %s', field, content)
            self.send_header(field, content)

        self.end_headers()

    def send_content(self, content):
        if content is not None:
            log.info('Server sending content: %d bytes', len(content))
            self.wfile.write(content)

    def finish_request(self):
        # Avoid same behaviour on next request
        if self.server.data.get('response_clear'):
            self.server.reset_response_data()

        if self.server.data.get('response_reset'):
            self.server.reset()

    @property
    def state(self):
        """Dict with the current server state"""
        return self.__dict__

    def update_state(self):
        """Copies current server state"""
        self.server.data.update(self.state)

    def save_history(self):
        """Create a new entry in history"""
        self.server.save_history()

    def __getattr__(self, name):
        # redirect all requests to handle_request
        # See implementation of BaseHTTPRequestHandler.handle_one_request
        if name.startswith('do_'):
            return self.handle_request
        return super(Handler, self).__getattribute__(name)


class Server(ThreadingMixIn, HTTPServer, Thread):
    """HTTP Server

    Starts in a child thread.
    Thread stops and closes when the parent process does.
    Handles each request on a new thread, *forks* on each request.

    Server state after each request can be checked as a `dict` through the
    thread-save attribute :attr:`data`, which is updated at the begining of
    each request. See :class:`Handler` and :class:`BaseHTTPRequestHandler` to
    see the information available on that `dict`.

    .. code::

        >> server.data
        {'requestline': 'GET /url HTTP/1.1', 'path': '/url', ...}

    if several requests are made, their state are kept in order in the history:

    .. code::

        >> server.history
        [
          {'path': '/first', ..},
          {'path': '/second', ..}
        ]

    *About multithreading:* It is necessary that each request gets serverd by
    a different thread, in case that more than one request is made at the same
    time. If any two requests are attended at the same time by the *same
    thread*, risk of deadlock exists.
    """
    def __init__(self, host, port,  scheme='http', handler=Handler):
        """Creates a new :class:`Server`

        :param host: Host for the server to listen.
        :param port: Port of the server to listen (should free).
        :param scheme: *(default: http)* 'http' or 'https'.
        :param handler: (default: :class:`Handler`) A
         :class:`BaseHTTPRequestHandler` class.
        """
        Thread.__init__(self)
        HTTPServer.__init__(self, (host, port), handler)
        self._data = {}
        self._history = []
        self._hooks = {}
        self.daemon = True  # finish along with parent process
        self.scheme = scheme

    @classmethod
    def start_server(cls, host, port):
        """Creates and starts a http :class:`Server`

        :param host: Host for the server to listen.
        :param port: Port of the server to listen (should not be in use).
        :returns: A created and started http :class:`Server`
        """
        log.info('Starting http server %s:%d', host, port)
        server = cls(host, port, 'http')
        server.start()
        return server

    @classmethod
    def start_ssl_server(cls, host, port, certfile, keyfile):
        """Creates and starts a https :class:`Server`

        :param host: Host for the server to listen.
        :param port: Port of the server to listen (should not be in use).
        :param certfile: Path to certificate file as
         accepted by :class:`HTTPServer`.
        :param keyfile: Path to private key file as accepted by
         :class:`HTTPServer`. Default it's bundled with *certfile*.
        :returns: A created and started https :class:`Server`
        """
        log.info('Starting https server %s:%d', host, port)
        log.debug('Using certfile: "%s"', certfile)
        log.debug('Using keyfile: "%s"', keyfile)
        server = cls(host, port, 'https')
        server.socket = ssl.wrap_socket(
            server.socket, server_side=True, certfile=certfile, keyfile=keyfile)
        server.start()
        return server

    @property
    def host(self):
        return self.server_address[0]

    @property
    def port(self):
        return self.server_address[1]

    @property
    def data(self):
        """Gives access to current server state `dict` (read-write)

        List of values that can be set to control the server behaviour:

        response_status
            An `int` with the status code of the next response.

        response_headers
            A `dict` or a `(k, v) tuple` with all the headers to be sent on
            the next response.

        response_content
            A `bytes` with the body of the next response.

        response_timeout
            A number with the time in seconds to wait before starting a response.

        response_clear
            `True` if server user state should be reset after responding.
            This is useful when responding with `3xx` redirections.

        response_reset
            `True` if server state should be totally reset after the response.

        value might be a callable, in which case, it is inmediately called
        with no arguments.
        """
        with lock:
            return self._data

    @property
    def hooks(self):
        """Gives access to server hooks

        Hooks will be called at different moments of the http processing,
        exposing handler data at the point and allowing to override response
        at will.

        Available hooks:

        before_request
            Arguments: ``()`` Called at the start of processing a new request.

        before_response
            Arguments: ``(request)`` Called after request has been parsed but not sent.

        after_response
            Arguments: ``(request, response)`` Called after the response has
            been created but no sent.

        after_request
            Arguments: ``(request, response)`` Called after a response has
            been sent back to the client.

        Return value is be ignored.
        """
        with lock:
            return self._hooks

    def register_hook(self, name, function):
        if not callable(function):
            raise ValueError('{} is not callable'.format(function))
        self.hooks[name] = function

    def process_hook(self, name, *args):
        function = self.hooks.get(name)
        if function:
            return function(*args)

    def reset(self):
        """Resets all server data

        This resets :attr:`data`, :attr:`history` and :attr:`hooks`.
        """
        with lock:
            self._data = {}
            self._history = []
            self._hooks = {}

    @property
    def history(self):
        """Gives access to all the server states in a `list` (read-only)"""
        with lock:
            return self._history

    def save_history(self):
        """Saves current data state in :attr:`history`"""
        # expand callable values
        with lock:
            self._data = {k: (v if not callable(v) else v())
                          for k, v in self.data.items()}
        self._history.append(dict(self.data))

    @property
    def response_data(self):
        """All user-defined response properties"""
        return {k: v for k, v in self.data.items() if k.startswith('response_')}

    def reset_response_data(self):
        for k in self.response_data:
            del self.data[k]

    def url(self, path):
        """Compose a full URL to the server from the url path:

        .. code::

            >> server.url('/test/url')
            http://127.0.0.1:8888/test/url
        """
        return "{}://{}:{}{}".format(self.scheme, self.host, self.port, path)

    def stop(self):
        """Stops the server thread"""
        self.shutdown()

    def run(self):
        try:
            log.info('Starting server')
            self.serve_forever()
        finally:
            log.info('Stopping server at: %s:%d', self.host, self.port)


@contextlib.contextmanager
def http_server(*args, **kwargs):
    """Context of a started HTTP :class:`Server`

    .. code::

        with http_server() as server:
            # use server

    See function :func:`start_server`.
    """
    server = start_server(*args, **kwargs)
    yield server
    server.stop()


@contextlib.contextmanager
def https_server(*args, **kwargs):
    """Context of a started HTTPS :class:`Server`

    .. code::

        with https_server() as server:
            # use server

    See function :func:`start_ssl_server`.
    """
    server = start_ssl_server(*args, **kwargs)
    yield server
    server.stop()


class HttpResponse(object):
    def __init__(self, status, headers, content):
        self.status = status
        self.headers = headers
        self.content = content

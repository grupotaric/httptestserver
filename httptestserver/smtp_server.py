# -*- coding: utf-8 -*-
"""
SMTP Server
-----------

SMTP python server which can be controlled from a different thread.

.. code::
    >>> server = start_smtp_server()
    >>> server.start()
    >>> sendemail('from@host.com', ['to@away.com'], 'Message...')
    >>> server.data['message']['subject']
    'Gotcha!'
    >>> server.close()
"""
import smtpd
import logging
import asyncore
import contextlib
import email.parser
from threading import Thread, RLock

lock = RLock()
log = logging.getLogger('httptestserver.smtp')

DEFAULT_HOST = '127.0.0.1'               # loopback
DEFAULT_PORT = 0                         # random port


def start_smtp_server(host=None, port=None):
    """Create a started Smtp server listening in *host*:*port*

    :param host: *(default: 127.0.0.1)* Host for the server to listen.
    :param port: *(default: random)* Port of the server to listen (should not be in use).
    :returns: A created and started :class:`SmtpServer`
    """
    return SmtpServer.start_server(host or DEFAULT_HOST, port or DEFAULT_PORT)


@contextlib.contextmanager
def smtp_server(*args, **kwargs):
    """Context of a started :class:`SmtpServer`

    .. code::

        with smtp_server() as server:
            # use server

    See function :func:`start_smtp_server`.
    """
    server = start_smtp_server(*args, **kwargs)
    yield server
    server.stop()


class SmtpServer(smtpd.SMTPServer, Thread):
    """SMTP Server

    Starts in a child thread as :class:`Server` does.

    Server state can be checked through de :attr:`SmtpServer.data` attribute
    after each request. See the attribute for a list of all available data.

    When several messages are sent at a time, the server state is still
    reachable through the :attr:`Server.history` attribute.

    *About multithreading:* The :mod:`asyncore` stdlib module that powers the
    python SMTP server does not quite like to be spawned in a different
    thread, feel free to open an issue in the project if you experience concurrency errors.
    """
    def __init__(self, host, port):
        Thread.__init__(self)
        smtpd.SMTPServer.__init__(self, (host, port), None)
        self._data = {}
        self._history = []
        self._continue = True
        self.daemon = True  # finish along with parent process

    @classmethod
    def start_server(cls, host, port):
        """Creates and starts a :class:`SmtpServer`

        :param host: Host for the server to listen.
        :param port: Port of the server to listen (should not be in use).
        :returns: A created and started http :class:`SmtpServer`
        """
        log.info('Starting http server %s:%d', host, port)
        server = cls(host, port)
        server.start()
        return server

    def process_message(self, peer, mailfrom, rcpttos, data):
        """Process a received smtp message"""
        self.update_state(peer, mailfrom, rcpttos, data)
        self.save_history()

    def update_state(self, peer, mailfrom, rcpttos, data):
        """Copies last message state"""
        self.data.update(dict(
            peer=peer,
            mailfrom=mailfrom,
            recipients=rcpttos,
            message_data=data,
            message=self.parse_message(data)
        ))

    def save_history(self):
        """Create a new entry in history"""
        self._history.append(dict(self.data))

    def parse_message(self, data):
        """Parse RFC 2822 message data

        :param bytes data: Full message data
        :returns: (headers, body)
        """
        return email.parser.Parser().parsestr(data)

    @property
    def data(self):
        """Gives access to current server state `dict` (read-write)

        List of values that can be set to control the server behaviour:

        message
            The parsed message in a :class:`email.message.Message` object.

        message_data
            Raw message bytestring as sent to the server

        peer
            Client ip address (host, port)

        mailfrom:
            Sender's email

        recipients:
            List of destination emails
        """
        with lock:
            return self._data

    def reset(self):
        with lock:
            self._data = {}
            self._history = []

    @property
    def history(self):
        """Gives access to all the server states in a `list` (read-only)"""
        with lock:
            return self._history

    @property
    def host(self):
        """Current binded host"""
        return self.socket.getsockname()[0]

    @property
    def port(self):
        """Current binded host"""
        return self.socket.getsockname()[1]

    def stop(self):
        """Stops the server thread"""
        self._continue = False
        self.close()

    def run(self):
        try:
            log.info('Starting server')
            while(self._continue):
                asyncore.loop(timeout=0.01, count=1)
        finally:
            log.info('Stopped server')

    def __getattribute__(self, attr):
        return object.__getattribute__(self, attr)

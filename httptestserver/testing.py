# -*- coding: utf-8 -*-

from .smtp_server import start_smtp_server
from .http_server import start_server, start_ssl_server


class ServerBase(object):
    """Base class for http server mixins"""

    server = None
    """Class level server instance"""

    default_path = '/testing/this'
    """Path for default url"""

    def url(self, path):
        """Returns full urls for the server from a path"""
        return self.server.url(path)

    @property
    def default_url(self):
        """Default url for testing"""
        return self.url(self.default_path)

    def setup(self):
        self.server.reset()


class HttpTestServer(ServerBase):
    """Mixin class for testing using a http server"""
    options = {}

    @classmethod
    def setupClass(cls):
        cls.server = start_server()


class HttpsTestServer(ServerBase):
    """Mixin class for testing using a https server"""
    options = {'verify': False}

    @classmethod
    def setupClass(cls):
        cls.server = start_ssl_server()


class SmtpTestServer(ServerBase):
    """Mixin class for testing using a smtp server"""

    @classmethod
    def setupClass(cls):
        cls.server = start_smtp_server()

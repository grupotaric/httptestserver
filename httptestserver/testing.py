# -*- coding: utf-8 -*-

from .server import start_server, start_ssl_server


class ServerBase(object):
    """Base para tests de server"""
    def url(self, path):
        return self.server.url(path)

    @property
    def default_path(self):
        return '/testing/this'

    @property
    def default_url(self):
        return self.url(self.default_path)


class HttpServerTest(ServerBase):
    options = {}

    @classmethod
    def setupClass(cls):
        cls.server = start_server()


class HttpsServerTest(ServerBase):
    options = {'verify': False}

    @classmethod
    def setupClass(cls):
        cls.server = start_ssl_server()

# -*- coding: utf-8 -*-

from hamcrest import *
from nose.tools import assert_raises

from httptestserver import (HttpServerTest, HttpsServerTest, Server,
                            http_server, https_server)

import requests


class ServerTestMixin(object):
    def request(self, *args, **kwargs):
        kwargs['verify'] = kwargs.get('verify', False)
        return requests.request(*args, **kwargs)

    def setup(self):
        self.server.reset()


class DataMixin(object):
    def test_it_should_send_headers(self):
        headers = {u'key': u'value'}

        self.request('GET', self.default_url, headers=headers)

        assert_that(self.server.data['headers'], has_entries(headers))

    def test_it_should_send_multiple_valued_headers(self):
        headers = dict([(u'key', u'value')] * 50)

        self.request('GET', self.default_url, headers=headers)

        assert_that(self.server.data['headers'], has_entries(headers))

    def test_it_should_have_all_data_in_dict(self):
        self.request('POST', self.default_url, data='content')

        assert_that(self.server.data, has_entries({
            'command': is_('POST'),
            'body': is_(b'content'),
            'rfile': has_property('read'),
            'wfile': has_property('write'),
            'path': is_(self.default_path),
            'request_version': is_('HTTP/1.1'),
            'client_address': contains('127.0.0.1', greater_than(0))
        }))

    def test_it_should_have_all_requests_stored(self):
        self.request('GET', self.server.url('/first'))
        self.request('POST', self.server.url('/second'))

        assert_that(self.server.history, contains(
            has_entries({'command': 'GET', 'path': '/first'}),
            has_entries({'command': 'POST', 'path': '/second'})
        ))


class MethodsMixin(object):
    """Tests sobre metodos/verbos HTTP

    Lista de metodos http
    Ver: http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
    """
    def test_it_should_send_GET_requests(self):
        self.request('GET', self.default_url)

        assert_that(self.server.data['command'], is_('GET'))

    def test_it_should_send_POST_requests(self):
        self.request('POST', self.default_url)

        assert_that(self.server.data['command'], is_('POST'))

    def test_it_should_send_PUT_requests(self):
        self.request('PUT', self.default_url)

        assert_that(self.server.data['command'], is_('PUT'))

    def test_it_should_send_HEAD_requests(self):
        self.request('HEAD', self.default_url)

        assert_that(self.server.data['command'], is_('HEAD'))

    def test_it_should_send_PATCH_requests(self):
        self.request('PATCH', self.default_url)

        assert_that(self.server.data['command'], is_('PATCH'))

    def test_it_should_send_DELETE_requests(self):
        self.request('DELETE', self.default_url)

        assert_that(self.server.data['command'], is_('DELETE'))

    def test_it_should_send_OPTIONS_requests(self):
        self.request('OPTIONS', self.default_url)

        assert_that(self.server.data['command'], is_('OPTIONS'))

    def test_it_should_send_TRACE_requests(self):
        self.request('TRACE', self.default_url)

        assert_that(self.server.data['command'], is_('TRACE'))

    def test_it_should_send_CONNECT_requests(self):
        self.request('CONNECT', self.default_url)

        assert_that(self.server.data['command'], is_('CONNECT'))


class ConnectionMixin(object):
    """Tests sobre el envio de datos a traves de la conexion"""

    def test_it_should_raise_timeout_if_response_delays(self):
        # Cuidado con este test, la granularidad del timeout
        # es en segundos y no en milisegundos
        self.server.data['response_timeout'] = 2

        with assert_raises(requests.exceptions.Timeout):
            self.request('GET', self.default_url, timeout=1)

    def test_it_should_return_given_response(self):
        expected_response = b'a'
        self.server.data['response_content'] = expected_response

        r = self.request('GET', self.default_url)

        assert_that(r.content, is_(expected_response))

    def test_it_should_return_success_statuses(self):
        expected_status = 200
        self.server.data['response_status'] = expected_status

        r = self.request('GET', self.default_url)

        assert_that(r.status_code, is_(expected_status))

    def test_it_should_not_loop_on_redirections(self):
        self.server.data['response_clear'] = True
        self.server.data['response_status'] = 301
        self.server.data['response_headers'] = {'Location': self.default_url}

        r = self.request('GET', self.default_url)

        assert_that(r.status_code, is_(200))

    def test_it_should_not_hold_previous_data(self):
        self.server.data['response_reset'] = True
        self.request('GET', self.default_url)

        assert_that(self.server.data, is_({}))


class HttpErrorsMixin(object):
    """Tests sobre errores HTTP devueltos por el servidor"""

    def test_it_should_return_user_error_codes(self):
        expected_status = 404
        self.server.data['response_status'] = expected_status

        r = self.request(method='GET', url=self.default_url)

        assert_that(r.status_code, is_(expected_status))

    def test_it_should_return_user_unauthorized_error_codes(self):
        expected_status = 401
        self.server.data['response_status'] = expected_status

        r = self.request(method='GET', url=self.default_url)

        assert_that(r.status_code, is_(expected_status))

    def test_it_should_return_user_forbidden_error_codes(self):
        expected_status = 403
        self.server.data['response_status'] = expected_status

        r = self.request(method='GET', url=self.default_url)

        assert_that(r.status_code, is_(expected_status))

    def test_it_should_return_user_not_found_error_codes(self):
        expected_status = 404
        self.server.data['response_status'] = expected_status

        r = self.request(method='GET', url=self.default_url)

        assert_that(r.status_code, is_(expected_status))

    def test_it_should_return_server_error_codes(self):
        expected_status = 500
        self.server.data['response_status'] = expected_status

        r = self.request(method='GET', url=self.default_url)

        assert_that(r.status_code, is_(expected_status))

    def test_it_should_return_unknown_error_codes(self):
        expected_status = 599
        self.server.data['response_status'] = expected_status

        r = self.request(method='GET', url=self.default_url)

        assert_that(r.status_code, is_(expected_status))

    def test_it_should_return_given_headers(self):
        headers = {'key': 'value'}
        self.server.data['response_headers'] = headers

        r = self.request('GET', self.default_url)

        assert_that(r.headers['key'], is_('value'))

    def test_it_should_return_given_multiple_headers(self):
        headers = [('key', 'value'), ('key', 'value')]
        self.server.data['response_headers'] = headers

        r = self.request('GET', self.default_url)

        assert_that(r.headers, has_entry('key', 'value, value'))


# actual test implementations
class TestHttp(HttpServerTest, ServerTestMixin, DataMixin, MethodsMixin,
               ConnectionMixin, HttpErrorsMixin):
    """Test http server"""


class TestHttps(HttpsServerTest, ServerTestMixin, DataMixin,
                MethodsMixin, ConnectionMixin, HttpErrorsMixin):
    """Test https server"""


class TestContexts(object):
    def test_it_starts_http_server(self):
        with http_server() as server:
            assert_that(server, all_of(
                is_(instance_of(Server)),
                has_property('scheme', is_('http'))
            ))

    def test_it_starts_https_server(self):
        with https_server() as server:
            assert_that(server, all_of(
                is_(instance_of(Server)),
                has_property('scheme', is_('https'))
            ))

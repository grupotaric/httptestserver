# -*- coding: utf-8 -*-
import time
from hamcrest import *
from nose.tools import assert_raises

from httptestserver import (HttpTestServer, HttpsTestServer, Server,
                            http_server, https_server, HttpResponse)
import requests


class ServerTestMixin(object):
    def request(self, *args, **kwargs):
        kwargs['verify'] = kwargs.get('verify', False)
        return requests.request(*args, **kwargs)


class DataMixin(object):
    def test_it_should_send_headers(self):
        headers = {'key': 'value'}

        self.request('GET', self.default_url, headers=headers)

        assert_that(self.server.data['headers'], has_entries(headers))

    def test_it_should_send_multiple_valued_headers(self):
        headers = dict([('key', 'value')] * 50)

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
        self.request('POST', self.server.url('/second'), data=b'data')

        assert_that(self.server.history, contains(
            has_entries({'command': 'GET', 'path': '/first'}),
            has_entries({'command': 'POST', 'path': '/second', 'body': b'data'})
        ))

    def test_it_should_read_user_config(self):
        user_data = {
            'response_timeout': 0.01,
            'response_status': 201,
            'response_headers': {'key': 'value'},
            'response_content': b'content',
            'response_clear': True,
        }
        self.server.data.update(user_data)

        self.request('GET', self.default_url)

        assert_that(self.server.history[0], has_entries(user_data))

    def test_it_should_read_user_config_from_callable(self):
        user_data = {
            'response_timeout': 0.01,
            'response_status': 201,
            'response_headers': {b'key': b'value'},
            'response_content': b'content',
            'response_clear': True,
        }
        self.server.data.update({k: self.fun(v) for k, v in user_data.items()})

        self.request('GET', self.default_url)

        assert_that(self.server.history[0], has_entries(user_data))

    def fun(self, value):
        return lambda: value


class MethodsMixin(object):
    """Test HTTP verbs/methods

    HTTP methods list:
    See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
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
    """Test real client sending data through a connection"""

    def test_it_should_raise_timeout_if_response_delays(self):
        # Beware, this test needs to have at least 1s granularity
        # due tu Windows time functions work in seconds
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
    """Tests HTTP server errors"""

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


class HooksTestMixin(object):
    def test_it_should_register_hooks(self):
        fun = lambda _: None
        self.server.register_hook('before_request', fun)
        self.server.register_hook('before_response', fun)
        self.server.register_hook('after_response', fun)
        self.server.register_hook('after_request', fun)

        assert_that(self.server.hooks, is_({
            'before_request': fun,
            'before_response': fun,
            'after_response': fun,
            'after_request': fun,
        }))

    def test_it_should_reject_non_callable_hooks(self):
        with assert_raises(ValueError):
            self.server.register_hook('before_request', None)

    def test_it_should_run_before_request_hook(self):
        self.it_should_call_hook('before_request')

    def test_it_should_run_before_response_hook(self):
        self.it_should_call_hook('before_response', instance_of(dict))

    def test_it_should_run_after_response_hook(self):
        self.it_should_call_hook(
            'after_response', instance_of(dict), instance_of(HttpResponse))

    def test_it_should_run_after_request_hook(self):
        self.it_should_call_hook(
            'after_request', instance_of(dict), instance_of(HttpResponse))

    def it_should_call_hook(self, name, *args):
        instance = {'called': False, 'args': None}

        def hook(*passed_args, **kwargs):
            instance['called'] = True
            instance['args'] = passed_args

        self.server.register_hook(name, hook)

        self.request('GET', self.default_url)

        assert_that(instance, has_entries({
            'called': True,
            'args': has_items(*args),
        }))


# actual test implementations
class TestHttp(HttpTestServer, ServerTestMixin, DataMixin, MethodsMixin,
               ConnectionMixin, HttpErrorsMixin, HooksTestMixin):
    """Test http server"""


class TestHttps(HttpsTestServer, ServerTestMixin, DataMixin,
                MethodsMixin, ConnectionMixin, HttpErrorsMixin, HooksTestMixin):
    """Test https server"""


class TestContexts(object):
    def test_it_starts_http_server(self):
        with http_server() as server:
            assert_that(server, all_of(
                is_(instance_of(Server)),
                has_property('scheme', is_('http'))
            ))

    def test_it_stops_http_server(self):
        with http_server() as server:
            assert_that(server.is_alive(), is_(True))

        time.sleep(0.01)
        assert_that(server.is_alive(), is_(False))

    def test_it_starts_https_server(self):
        with https_server() as server:
            assert_that(server, all_of(
                is_(instance_of(Server)),
                has_property('scheme', is_('https'))
            ))

    def test_it_stops_https_server(self):
        with https_server() as server:
            assert_that(server.is_alive(), is_(True))

        time.sleep(0.01)
        assert_that(server.is_alive(), is_(False))


class TestHttpServer(object):
    """Test http server class methods"""
    def test_it_should_have_no_initial_data(self):
        assert_that(self.server, has_property('data', is_({})))

    def test_it_should_have_no_initial_history(self):
        assert_that(self.server, has_property('history', is_([])))

    def test_it_should_have_no_initial_hooks(self):
        assert_that(self.server, has_property('hooks', is_({})))

    def test_it_should_have_default_http_scheme(self):
        assert_that(self.server, has_property('scheme', is_('http')))

    def setup(self):
        self.server = Server('0.0.0.0', 0)

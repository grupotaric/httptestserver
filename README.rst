HttpTestServer
**************

HTTP/HTTPS server which can be run within a Python process. Runs in a
different thread along with the application exposing a simple thread-safe API,
so the calling code can control of how the server behaves.

Sometimes integration tests cannot do with mocking the ``socket.socket``
function avoiding real networking, this partially solves that problem by
providing a real server which is as easy to use and can perform real network
communication in a controlled and reliable way.

.. code:: python

    import requests
    from httptestserver import HttpsServerTest

    class TestApplication(HttpsServerTest):

        # Test what was actually get by the server
        def test_it_should_send_headers(self):
            headers = {'key': 'value'}

            requests.get(self.default_url, headers=headers)

            assert self.server.data['headers']['key'] == 'value'

        # Control server responses
        def test_it_should_parse_json_response(self):
            self.server.data['headers'] = {'Content-Type': 'application/json'}
            self.server.data['response_content'] = "{'key': 'value'}"

            response = requests.get(self.default_url)

            assert response.json() == {'key': 'value'}

        # Make the server behave as you want
        def test_it_should_raise_timeout_at_2s_wait(self):
            self.server.data['response_timeout'] = 2

            try:
                requests.get(self.default_url, timeout=1)
            except requests.exceptions.Timeout:
                pass
            else:
                assert False

        # Access to server's requests/responses history
        def test_it_should_make_two_requests(self):
            self.server.reset()

            requests.get(self.default_url)
            requests.get(self.default_url + '2')

            assert len(self.server.history) == 2
            assert self.server.history[-1]['path'] == self.default_url + '2'


Features:

* Runs in a different thread at the same time of your tests.
* Control server responses and behaviour.
* Access to server internal state and data after or during the request.
* HTTPs support, it bundles a self-signed certificate useful for testing.
* History of all server performed requests/responses.


Api
===

Functions which return a running server instance:

.. autofunction:: start_server
.. autofunction:: start_ssl_server

Context managers for short in-place usage:

.. autofunction:: http_server
.. autofunction:: https_server

The :class:`Server` class, with all the available functionality:

.. autoclass:: Server
    :members:


The default handler is :class:`Handler` but it can be subclassed and extended:

.. autoclass:: httptestserver.server.Handler
    :members:

Some mixings to start the server and use it directly from tests.

.. autoclass:: HttpServerTest
    :members:


.. autoclass:: HttpsServerTest
    :members:


Development
===========

In order get a development environment, create a virtualenv and install the
desired requirements.

.. code:: bash

    virtualenv env
    env/bin/activate
    pip install -r dev-requirements.txt


The included certificate was generated using SSL:

.. code:: bash

    openssl req -new -x509 -keyout server.pem -out server.pem -days 40000 -nodes


Tests
-----

To run the tests just use **tox** or **nose**:

.. code:: bash

    tox


.. code:: bash

    nosetests


Documentation
-------------

To generate the documentation change to the ``docs`` directory and run make.
You need to install the ``sphinx`` and ``changelog`` packages in order to be
able to run the makefile.


.. code:: bash

    cd docs
    make html
    open build/html/index.html
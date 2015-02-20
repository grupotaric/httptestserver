HttpTestServer
**************

.. image:: https://badge.fury.io/py/httptestserver.svg
    :target: http://badge.fury.io/py/httptestserver
    :alt: Latest Pypi version

.. image:: https://readthedocs.org/projects/httptestserver/badge/?version=latest
    :target: https://readthedocs.org/projects/httptestserver/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/grupotaric/httptestserver.svg?branch=master
    :target: https://travis-ci.org/grupotaric/httptestserver
    :alt: Last build status

HTTP(s) and SMTP servers which can be run within a Python process. Serving
from different thread along with application and tests, exposing a simple
thread-safe API, so the calling code can control how the server behaves.

Sometimes integration tests cannot do with mocking the ``socket.socket``
function avoiding real networking, this partially solves the problem by
providing a real server which is easy to use and can perform real network
communication in a controlled and reliable way.

Features:

* Runs in a different thread along with your tests.
* Control server responses and behaviour.
* Access to server internal state and data after or during the request.
* HTTPs support, it bundles a self-signed certificate useful for testing.
* SMTP support which will collect and parse all your outgoing email.
* History of all performed requests/responses.

Supports ``python`` *2.7* *3.2*, *3.3* and *3.4*


Functions
---------

Functions that return a running server instance:

.. code:: python

    >>> server = start_server()
    >>> server.host
    '127.0.0.1'


Or context managers for limited use:

.. code:: python

    >>> with http_server() as server:
    ...     server.host
    '127.0.0.1'

.. code:: python

    >>> with smtp_server() as server:
    ...     server.inbox
    []


Mixin classes
-------------

Mixins that include an working server as ``self.server``.


.. code:: python

    import requests
    from httptestserver import HttpsTestServer

    class TestApplication(HttpsTestServer):

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
            requests.get(self.default_url)
            requests.get(self.default_url + '2')

            assert len(self.server.history) == 2
            assert self.server.history[-1]['path'] == self.default_url + '2'


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

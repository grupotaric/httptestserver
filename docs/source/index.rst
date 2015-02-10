.. httptestserver documentation master file, created by
   sphinx-quickstart on Wed Nov 12 10:21:07 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. module:: httptestserver

.. include:: ../../README.rst

Api
===

Functions which return a running server instance:

.. autofunction:: start_server
.. autofunction:: start_ssl_server
.. autofunction:: start_smtp_server

Context managers for short in-place usage:

.. autofunction:: http_server
.. autofunction:: https_server
.. autofunction:: smtp_server

The :class:`Server` class, with all the available functionality for http and
https:

.. autoclass:: Server
    :members:

The default handler is :class:`Handler` but it can be subclassed and extended:

.. autoclass:: httptestserver.http_server.Handler
    :members:

The :class:`SmtpServer` class helps to test real application mailing:

.. autoclass:: SmtpServer
    :members:

Some mixins to start the server and use it directly from tests.

.. autoclass:: HttpTestServer
    :members:
    :undoc-members:


.. autoclass:: HttpsTestServer
    :members:
    :undoc-members:


.. autoclass:: SmtpTestServer
    :members:
    :undoc-members:


.. include:: ../../HISTORY.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

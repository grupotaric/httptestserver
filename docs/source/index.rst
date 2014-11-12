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
    :undoc-members:


.. autoclass:: HttpsServerTest
    :members:
    :undoc-members:


.. include:: ../../HISTORY.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


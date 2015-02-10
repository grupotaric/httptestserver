Changes
=======

List of all the changes throughout different versions.

.. changelog::
    :version: 0.1.1
    :released: 2014-11-13

    Adds initial SMTP support

    .. change::
       :tags: feature

       Adds SMTP server and testing tools

       | Added new class :class:`SmtpServer`
       | Added new class :class:`SmtpTestServer`
       | Added new function :func:`start_smtp_server`
       | Added new context manager :func:`smtp_server`

    .. change::
        :tags: feature

       Renames ``server`` module to ``http_server``

    .. change::
        :tags: error

       Saves http request in history before processing response.

       The processing method can very well not return and block or raise an
       exception, losing thus the server state for that request.

    .. change::
        :tags: feature

       Renames :mod:`http_server` logger to ``httptestserver.http``

    .. change::
        :tags: feature

       Adds default setup function to :class:`.ServerBase` that resets the
       current server state.

       It does not quite make sense to have the :class:`~Server.history` save
       ALL ever made requests between tests.

.. changelog::
    :version: 0.1.1
    :released: 2014-11-13

    Name update.

    .. change::
       :tags: feature

       Fixes name incoherence for testing mixins.

       Renames ``HttpServerTest`` to :class:`HttpTestServer`
       Renames ``HttpsServerTest`` to :class:`HttpsTestServer`


.. changelog::
    :version: 0.1.0
    :released: 2014-11-12

    Initial version

    .. change::
       :tags: feature

       Adds :class:`Server` class.

    .. change::
       :tags: feature

       Adds :func:`start_server` and :func:`start_ssl_server` convenience
       functions.

    .. change::
       :tags: feature

       Adds :func:`http_server` and :func:`https_server` context managers.

    .. change::
       :tags: feature

       Adds :func:`HttpServerTest` and :func:`HttpsServerTest` mixins classes
       to be used in testing.

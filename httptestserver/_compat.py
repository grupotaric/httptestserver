import sys
import collections


PY2 = sys.version_info[0] == 2


if PY2:
    from SocketServer import ThreadingMixIn
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
else:
    from socketserver import ThreadingMixIn
    from http.server import HTTPServer, BaseHTTPRequestHandler


def iteritems(iterable):
    if isinstance(iterable, collections.Mapping):
        return iterable.iteritems() if PY2 else iterable.items()
    else:
        return iterable

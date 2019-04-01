#!/usr/bin/env python3


class ReverseProxyMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.app = self.wsgi_app.__self__

    def __call__(self, environ, start_response):
        """
        Fixes the behaviour of flask core applications whilst behind a reverse proxy.

        :param environ:
        :param start_response:
        :return:
        """
        server = environ.get("HTTP_X_FORWARDED_SERVER", None)

        if server is not None:
            environ["HTTP_HOST"] = server

        return None

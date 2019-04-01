#!/usr/bin/env python3

from .AuthMiddleware import AuthMiddleware
from .FilterMiddleware import FilterMiddleware
from .IsolationMiddleware import IsolationMiddleware
from .ReverseProxyMiddleware import ReverseProxyMiddleware


class Handler(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.middleware = [
            FilterMiddleware(self.wsgi_app),
            ReverseProxyMiddleware(self.wsgi_app),
            AuthMiddleware(self.wsgi_app),
            IsolationMiddleware(self.wsgi_app),
        ]

    def __call__(self, environ, start_response):
        """
        Cycles through all our middleware and calls them in order.

        :param environ:
        :param start_response:
        :return: Middleware response if any, else wsgi_app response
        """

        # Bypass all middleware for /core/cse
        if environ["PATH_INFO"] == "/core/cse":
            return self.wsgi_app(environ, start_response)

        for middleware in self.middleware:
            res = middleware(environ, start_response)

            if res is not None:
                return res

        return self.wsgi_app(environ, start_response)

#!/usr/bin/env python3

from .AuthMiddleware import AuthMiddleware
from .FilterMiddleware import FilterMiddleware
from .IsolationMiddleware import IsolationMiddleware

class Handler(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.middleware = [
            FilterMiddleware(self.wsgi_app),
            AuthMiddleware(self.wsgi_app),
            IsolationMiddleware(self.wsgi_app)
        ]

    def __call__(self, environ, start_response):
        for middleware in self.middleware:
            res = middleware(environ, start_response)

            if res is not None:
                return res

        return self.wsgi_app(environ, start_response)

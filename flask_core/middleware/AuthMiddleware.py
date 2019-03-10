#!/usr/bin/env python3


class AuthMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.cse_endpoint = wsgi_app.__self__.config['CSE_AUTH_ENDPOINT']
        self.assertion_pub_key = wsgi_app.__self__.config['CSE_AUTH_PUBKEY']

    def __call__(self, environ, start_response):
        # Check if we have any cookies available in this session
        if 'HTTP_COOKIE' not in environ:
            start_response('302 Forbidden', [])
            return [
                b'Forbidden'
            ]

        return self.wsgi_app(environ, start_response)

    def _check_assertion(self, cookie):
        pass

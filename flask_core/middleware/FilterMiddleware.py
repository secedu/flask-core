#!/usr/bin/env python3


class FilterMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.blacklist = ["sqlmap", "dirbuster"]

    def __call__(self, environ, start_response):
        try:
            if any((x for x in self.blacklist if x in environ["HTTP_USER_AGENT"].lower())):
                start_response("503 Internal Server Error", [])
                return [b"Something went wrong."]
        except KeyError:
            pass
        return None

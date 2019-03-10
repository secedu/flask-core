#!/usr/bin/env python3

from http.cookies import SimpleCookie


class AuthMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.app = wsgi_app.__self__
        self.cse_endpoint = self.app.config["CSE_AUTH_ENDPOINT"]
        self.assertion_pub_key = self.app.config["CSE_AUTH_PUBKEY"]

    def __call__(self, environ, start_response):
        if environ["PATH_INFO"] != "/core/cse" and "HTTP_COOKIE" not in environ:
            return self._require_auth(environ, start_response)

        if environ["PATH_INFO"] == "/core/cse":
            return self.wsgi_app(environ, start_response)

        # Verify that the cookies are valid
        cookie_store = SimpleCookie()
        cookie_store.load(environ["HTTP_COOKIE"])

        try:
            zid = next((i for i in cookie_store.items() if i[0] == "zid"))[1].value
            token = next((i for i in cookie_store.items() if i[0] == "token"))[1].value
        except StopIteration:
            return self._require_auth(environ, start_response)

        if zid not in self.app.active_sessions or self.app.active_sessions[zid] != token:
            return self._require_auth(environ, start_response)

        return self.wsgi_app(environ, start_response)

    def _check_assertion(self, cookie):
        pass

    def _require_auth(self, environ, start_response):
        server_name = (
            environ["HTTP_X_FORWARDED_SERVER"] if "HTTP_X_FORWARDED_SERVER" in environ else environ["HTTP_HOST"]
        )

        start_response("302 Temporary Redirect", [("Location", f"{self.cse_endpoint}?t=http://{server_name}/core/cse")])

        return [b"Authentication required, redirecting.."]

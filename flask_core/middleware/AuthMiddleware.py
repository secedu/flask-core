#!/usr/bin/env python3


class AuthMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.app = wsgi_app.__self__
        self.cse_endpoint = self.app.config["CSE_AUTH_ENDPOINT"]
        self.assertion_pub_key = self.app.config["CSE_AUTH_PUBKEY"]

        # Register the zID into the session when
        if self.app.config["ENABLE_AUTH"]:
            self.app.before_request(self._register_zid)

    def __call__(self, environ, start_response):
        """
        Enforces authentication for all requests hitting this flask application.

        :param environ:
        :param start_response:
        :return:
        """
        if not self.app.config["ENABLE_AUTH"] or environ["PATH_INFO"] == "/core/cse":
            return None

        if not self.app.config["AUTH_CHECKER"].check_auth(environ):
            return self.app.config["AUTH_CHECKER"].require_auth(environ, start_response)

        return None

    def _require_auth(self, environ, start_response):
        """
        Redirects the user to the authentication endpoint.

        TODO: make the redirect adaptable? Authcloak may also depreciate this.. this shouldn't be here since it's
        strictly CSE only

        :param environ:
        :param start_response:
        :return:
        """
        server_name = environ["HTTP_HOST"]

        start_response("302 Temporary Redirect", [("Location", f"{self.cse_endpoint}?t=http://{server_name}/core/cse")])

        return [b"Authentication required, redirecting.."]

    @staticmethod
    def _register_zid():
        """
        This operates in the flask request context. We pass in the WSGI environ into the configured auth_checker and
        register the provided zID into the request-scoped globals.

        :return: None
        """
        from flask import g, request, current_app

        g.zid = current_app.config["AUTH_CHECKER"].check_auth(request.environ)

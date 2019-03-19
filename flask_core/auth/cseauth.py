#!/usr/bin/env python3
from http.cookies import SimpleCookie

from .checker import Checker


class CSEAuth(Checker):
    """
    This authentication method relies on CSE sending us a signed zID with a pre-shared key.
    """

    def __init__(self):
        super().__init__()

        # Map of zid -> token
        self.active_sessions = {}

    def do_auth(self, **kwargs):
        try:
            zid = kwargs["zid"]
            token = kwargs["token"]
        except KeyError:
            raise RuntimeError("do_auth called without zid or token")

        self.active_sessions[zid] = token

    def check_auth(self, environ):
        # Verify that the cookies are valid
        cookie_store = SimpleCookie()
        try:
            cookie_store.load(environ["HTTP_COOKIE"])
        except:
            return None

        try:
            zid = next((i for i in cookie_store.items() if i[0] == "zid"))[1].value
            token = next((i for i in cookie_store.items() if i[0] == "token"))[1].value
        except StopIteration:
            return None

        if zid not in self.active_sessions or self.active_sessions[zid] != token:
            return None

        return zid

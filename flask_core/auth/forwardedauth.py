#!/usr/bin/env python3
from .checker import Checker


class ForwardedAuth(Checker):
    """
    This auth method relies on the upstream server providing authenticating and simply
    giving us an authenticated header.
    """

    def __init__(self):
        super().__init__()

    def check_auth(self, environ):
        return environ["HTTP_X_REMOTE_USER"]

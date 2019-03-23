#!/usr/bin/env python3

import os
import secrets
import logging
import textwrap

from flask_core.auth.cseauth import CSEAuth

logger = logging.getLogger(__name__)


class Config(object):
    """
    Core config for our application.
    """

    def __init__(self, **kwargs):
        """
        Create the configuration object.

        Config options are overridable through specifying keyword arguments as needed.

        :param kwargs: Options to set
        """

        # Sensible defaults
        self.STATIC_URL_PATH = "/static"
        self.THEME = "flatly"
        self.LOGIN_FORM = False
        self.TITLE = "Flask Core"
        self.NAVBAR = []
        self.SECRET_KEY = secrets.token_bytes(16)
        self.DEBUG = bool(os.environ.get("DEBUG", False))

        self.FLASK_CORE_ENABLE_AUTH = True
        if os.environ.get("FLASK_CORE_ENABLE_AUTH", "").lower() == 'false':
            self.FLASK_CORE_ENABLE_AUTH = False

        if not self.FLASK_CORE_ENABLE_AUTH:
            logger.error("Auth disabled, auto disabling database isolation")
            self.FLASK_CORE_ISOLATION_ENABLED = False
        
        # Make the auth checker pluggable - default to cse for now
        self.AUTH_CHECKER = CSEAuth()

        # CSE auth verification stuff
        self.CSE_AUTH_ENDPOINT = "http://cgi.cse.unsw.edu.au/~cs6443/auth/"
        self.CSE_AUTH_PUBKEY = textwrap.dedent(
            """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq31fBpVAMbU/u6LQO2m3
kFNPAOodBiiJ1jpLghiasZkHtXiz2DZ1yc+Wuby5aJzlPt3UIq13wLwqzyn0aICU
YFUUxcohRIsUFJH5a2lQWCKt9KVnA4vlg3xOx41Bx+hD4ifz9cJCM/ct2+UKquz/
R57F5j9myKFvIbNWR2rCJua7Vj7BYpe14jsNnvI3FCQM8SJLjKeBoBqo3/Y87PSG
fghw8tvQVcPPujtanUB74SEu0N12HBoYsfKOa3XrF0tae7CYZDFpUQCRfvLjEXpF
S9sT6rVgrjWSogM1nu/OfdjMf4X0ifuhrptHl6WfB+yhyxXJwJqZl3l5uTHMyemN
VQIDAQAB
-----END PUBLIC KEY-----
"""
        ).encode("utf8")

        # Use any user provided config opts
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Try to get user specified config opts, and if they don't exist read from environment
        try:
            self.FLAG = getattr(self, "FLAG", None) or os.environ["FLAG"]
            self.FLAG_SECRET = getattr(self, "FLAG_SECRET", None) or os.environ["FLAG_SECRET"]
            self.DB_CONNECTION_STRING = (
                getattr(self, "DB_CONNECTION_STRING", None) or os.environ["DB_CONNECTION_STRING"]
            )
        except KeyError as e:
            raise RuntimeError(f"Required config option {e} not set and not provided from environment.")

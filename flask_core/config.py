#!/usr/bin/env python3

import os
import secrets
import logging
import textwrap

from flask_core.auth.cseauth import CSEAuth
from distutils.util import strtobool

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

        self.ENABLE_AUTH = strtobool(os.environ.get("FLASK_CORE_ENABLE_AUTH", "True"))
        self.ENABLE_ISOLATION = strtobool(os.environ.get("FLASK_CORE_ENABLE_ISOLATION", "True"))

        self.ISOLATION_TABLES = [t for t in os.environ.get("FLASK_CORE_ISOLATE_TABLES", "").split(",") if t.strip()]

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

        self.AUTO_GENERATED_FLAGS = (
            getattr(self, "AUTO_GENERATED_FLAGS", None) or os.environ.get("FLASK_CORE_AUTO_GENERATED_FLAGS", True)
        )

        if not self.ENABLE_AUTH and self.ENABLE_ISOLATION:
            logger.warning("Auth disabled, auto disabling database isolation and auto flag generation")
            self.ENABLE_ISOLATION = False
            self.AUTO_GENERATED_FLAGS = False
        # Try to get user specified config opts, and if they don't exist read from environment
        try:
            self.FLAG_IDS = (getattr(self, "FLAG_IDS", None) or os.environ["FLAG_IDS"]).split(",")
            self.FLAG_WRAP = getattr(self, "FLAG_WRAP", None) or os.environ["FLAG_WRAP"]
            self.FLAG_SECRET = getattr(self, "FLAG_SECRET", None) or os.environ["FLAG_SECRET"]
            self.DB_CONNECTION_STRING = (
                getattr(self, "DB_CONNECTION_STRING", None) or os.environ["DB_CONNECTION_STRING"]
            )
        except KeyError as e:
            raise RuntimeError(f"Required config option {e} not set and not provided from environment.")

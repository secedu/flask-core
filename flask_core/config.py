#!/usr/bin/env python3

import os
import secrets
import logging
import textwrap
from urllib.parse import urlparse 

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
            url = getattr(self, "DB_CONNECTION_URL", None) or os.environ["DB_CONNECTION_URL"]
            parsed = urlparse(url)
            self.DB_CONFIG = {
                "HOST": parsed.hostname,
                "DIALECT": parsed.scheme,
                "ROOT_USERNAME": parsed.username,
                "ROOT_PASSWORD": parsed.password,
                "SCHEMA_FILE": getattr(self, "DB_SCHEMA_FILE", None) or os.environ["DB_SCHEMA_FILE"],
                "MODE": getattr(self, "DB_MODE", None) or os.environ["DB_MODE"],
                "BASE": parsed.path[1:]
            }

            # check DB_MODE
            if self.DB_CONFIG["MODE"] in ["GLOBAL", "STUDENT_ISOLATED"]:
                raise RuntimeError(f"Required config option DB_MODE must be either GLOBAL or STUDENT_ISOLATED")
            # read schema
            with open(self.DB_CONFIG["SCHEMA_FILE"],"r") as f:
                self.DB_CONFIG["SCHEMA"] = f.read()
        except KeyError as e:
            raise RuntimeError(f"Required config option {e} not set and not provided from environment.")

#!/usr/bin/env python3

import os
import secrets
import logging

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
        self.CSE_AUTH_PUBKEY = \
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMPXnWOREIV3X6mkPLLn5xjYZxMT/Nld2owilXuc3n6E assertion_pkey_100319"

        # Use any user provided config opts
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Try to get user specified config opts, and if they don't exist read from environment
        try:
            self.FLAG = getattr(self, 'FLAG', None) or os.environ['FLAG']
            self.FLAG_SECRET = getattr(self, 'FLAG_SECRET', None) or os.environ["FLAG_SECRET"]
            self.DB_CONNECTION_STRING = getattr(self, 'DB_CONNECTION_STRING', None) or os.environ["DB_CONNECTION_STRING"]
        except KeyError as e:
            raise RuntimeError(f'Required config option {e} not set and not provided from environment.')

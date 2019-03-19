#!/usr/bin/env python3

from abc import ABC


class Checker(ABC):
    def do_auth(self, **kwargs):
        """
        Abstract method used to do authentication of users if needed.

        If the authentication mechanism doesn't require Flask Core to handle tokens, this function can be stubbed out.

        :param kwargs:
        :return:
        """

        pass  # this function is doesn't strictly need to be implemented

    def check_auth(self, environ):
        """
        Abstract method that should return zID if the user is authenticated

        :param environ: WSGI environ
        :return: zID if authenticated, otherwise None
        """

        raise NotImplementedError

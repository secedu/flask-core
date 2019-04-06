#!/usr/bin/env python3

import base64
import textwrap

import cryptography
import secrets

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from flask import request, render_template, current_app, flash, make_response, g

from flask_core.auth.cseauth import CSEAuth
from . import bp as app  # Note that app = blueprint, current_app = flask context
from flask_core.flag import check_flag


@app.route("/")
def home():
    return render_template("core/home.html")


@app.route("/wipedb", methods=["GET", "POST"])
def wipe():
    if request.method == "POST":
        try:
            current_app.db.execute(f"DROP SCHEMA {g.zid} CASCADE")

            flash("DB Wiped.", "success")
        except ValueError:
            flash("Something Went Wrong :(", "danger")

    return render_template("core/wipedb.html")


@app.route("/checker", methods=["GET", "POST"])
def checker():
    if g.zid is None:
        tag = secrets.token_hex(10)
        current_app.logger.error("[%s] Failed to get zID for request, g.zid is None.", tag)

        return "Report this to #comp6443-problems with this tag: %s" % tag

    if request.method == "POST":
        if check_flag(g.zid, request.form["flag"]):
            flash("That is a flag!", "success")
        else:
            flash("Not a flag", "danger")

    return render_template("core/check.html")


@app.route("/cse")
def handle_cse():
    """
    Handles CSE authentication.

    Checks if the provided assertion has been signed with a trusted private key. If so, sign an
    assertion and pass it back.

    :return:
    """

    # Check if we're using the CSE auth checker
    if type(current_app.config.AUTH_CHECKER) is not CSEAuth:
        return "This incident has been reported.", 403

    if any((x for x in ["a", "s"] if x not in request.args)):
        return "Invalid authorization request.", 400

    signature = base64.b64decode(request.args["s"])

    key = load_pem_public_key(current_app.config["CSE_AUTH_PUBKEY"], backend=default_backend())

    try:
        key.verify(signature, request.args["a"].encode("utf8"), padding.PKCS1v15(), hashes.SHA1())
    except cryptography.exceptions.InvalidSignature:
        return "Tampered payload.", 403

    [zid, timestamp] = request.args["a"].split(":")

    # TODO: expire on timestamp

    resp = make_response(
        textwrap.dedent(
            """
        <meta http-equiv="refresh" content="1;url=/" />
        Successfully authenticated! We'll take you back now.
    """
        )
    )
    user_token = secrets.token_hex(32)

    current_app.config["AUTH_CHECKER"].do_auth(zid=zid, token=user_token)

    resp.set_cookie("zid", zid)
    resp.set_cookie("token", user_token)

    return resp

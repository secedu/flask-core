#!/usr/bin/env python3

import base64
import textwrap

import cryptography
import secrets

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from flask import (
    render_template_string,
    request,
    render_template,
    current_app,
    flash,
    redirect,
    url_for,
    session,
    make_response,
)
from . import bp as app  # Note that app = blueprint, current_app = flask context

@app.route("/")
def home():
    return "Flask Core - Common routes"

@app.route("/nuke_db")
def nuke_db():
    #TODO: this

@app.route("/cse")
def handle_cse():
    """
    Handles CSE authentication.

    Checks if the provided assertion has been signed with a trusted private key. If so, sign an
    assertion and pass it back.

    :return:
    """

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



    # 0. Set up and early exit
    config = current_app.config["DB_CONFIG"]
    zid_db_name = f"{zid}_{config["BASE"]}"
    if config["MODE"] == "GLOBAL":
        current_app.db = current_app.global_db
    else:
        # 1. check if zid exists db 
        res = current_app.db.execute("SELECT * FROM information_schema.tables WHERE table_name=%s",(zid_db_name,)).first()
        if res is None:
            create_user_db(zid)
        # 2. connect to db as zid
    

    if config["DB_MODE"] == "STUDENT_ISOLATED":
        passwd = secrets.token_hex(16)
        session.db_name = f"{zid}_{config["BASE"]}"
        db_config = current_app.config["DB_CONFIG"]
        current_app.db.execute("CREATE USER %s WITH PASSWORD %s",(zid,passwd,))
        current_app.db.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {session.db_name} TO {zid}")
        current_app.db.execute(f"CREATE DATABASE {session.db_name} WITH TEMPLATE {db_config["DB_BASE"]} OWNER {zid}")
        session.db = create_engine(f"{db_config["DB_PROTOCOL"]}://{zid}:{passwd}@{db_config["DB_HOST"]}/{session.db_name}")
    else:
        session.db = current_app.global_db
    
    if zid in current_app.active_sessions:
        current_app.active_sessions[zid].kill()
    
    current_app.active_sessions[zid] = session

    resp.set_cookie("zid", zid)
    resp.set_cookie("token", user_token)

    return resp

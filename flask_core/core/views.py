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
    jsonify
)
from . import bp as app  # Note that app = blueprint, current_app = flask context
from urllib.parse import urlparse
import natural.date
import subprocess

# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

@app.route("/")
def home():
    return render_template("core/home.html")

@app.route("/heartbeat")
def heartbeat_public():
    '''
    Returns basic information on if a site is working or not
    '''
    db_name = urlparse(current_app.config["DB_CONNECTION_STRING"]).path[1:]
    [db_use_bytes] = current_app.db.execute(f"select pg_database_size('{db_name}')").first()
    db_use = (db_use_bytes/1e+9)*100
    db_use_pretty = sizeof_fmt(db_use_bytes)
    import time 
    
    uptime = natural.date.compress(time.time() - current_app.start_time)
    pids = subprocess.check_output("ps -A | grep gunicorn | head -n2 | cut -d' ' -f2", shell=True)
    pids = str(pids,"utf-8")
    pids = list(filter(lambda x: x != "",pids.split("\n")))
    memory = {}
    for pid in pids:
        memory[pid] = str(subprocess.check_output(f"ps -o '%mem' {pid}", shell=True),"utf-8").replace("\n"," ")
    
    g = {
        'processes': int(subprocess.check_output("ps -A | grep gunicorn | wc -l", shell=True)) - 2,
        'pids': pids,
        'memory': memory
    }

    return render_template("core/heartbeat.html",
        db_use=db_use,
        db_use_pretty=db_use_pretty,
        uptime=uptime,
        ghealth=g,
        all_flags_ok=flags_ok)

@app.route("/heartbeat/detail")
def heartbeat_private():
    '''
    Returns a detailed json response of the health of the challange
    '''
    return jsonify({
        
    })

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

    current_app.config["AUTH_CHECKER"].do_auth(zid=zid, token=user_token)

    resp.set_cookie("zid", zid)
    resp.set_cookie("token", user_token)

    return resp

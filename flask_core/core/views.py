#!/usr/bin/env python3

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


@app.before_request
def check_core_auth():
    if 'CORE_TOKEN' not in current_app.config or 'TOKEN' not in request.cookies:
        return 'This subdirectory is not in scope.', 400

    if current_app.config['CORE_TOKEN'] != request.cookies['TOKEN']:
        return 'This subdirectory is not in scope.', 403


@app.route("/")
def home():
    return 'Flask Core - Common routes'


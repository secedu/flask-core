#!/usr/bin/env python3

from flask import Blueprint

bp = Blueprint(
    "core",
    __name__,
    static_folder="static",
    static_url_path="/static/core",
    url_prefix="/core",
    template_folder="templates",
)

from . import views
from . import models

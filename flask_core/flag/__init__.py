import hashlib


def gen_flag(zid, flag_id):
    from flask import current_app
    secret = current_app.config["FLAG_SECRET"]
    wrapper = current_app.config["FLAG_WRAP"]
    s = secret + zid + str(flag_id)
    b = bytes(s, "utf-8")
    return f"{wrapper}{{{hashlib.sha256(b).hexdigest()}}}"


def check_flag(zid, flag):
    from flask import current_app
    return any((current_app.gen_flag(zid, f) == flag for f in current_app.config["FLAG_IDS"]))

import hashlib

from flask import current_app, g


def gen_flag(zid, flag_id):
    secret = current_app.config["FLAG_SECRET"]
    wrapper = current_app.config["FLAG_WRAP"]

    if not zid:
        raise RuntimeError("Attempted to generate a flag with null zID.")

    s = secret + zid + str(flag_id)
    b = bytes(s, "utf-8")

    return f"{wrapper}{{{hashlib.sha256(b).hexdigest()}}}"


def check_flag(zid, flag):
    if not zid:
        raise RuntimeError("Attempted to check flag with null zID.")

    return any((gen_flag(zid, f) == flag for f in current_app.config["FLAG_IDS"]))


def grep_flag(response):
    if not current_app.config["AUTO_GENERATED_FLAGS"]:
        return response

    try:
        response.direct_passthrough = False
        data = str(response.get_data(), "utf-8")
        zid = g.zid

        for f in current_app.config["FLAG_IDS"]:
            data = data.replace(f"flag{{_{f}}}", gen_flag(zid, f))

        data = bytes(data, "utf-8")
        response.set_data(data)
    except UnicodeDecodeError:
        pass

    return response

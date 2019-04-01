# Flask Core

This is a reusable core used to back COMP6443 applications.

## Overview

Flask Core is intended to be an installable Pip package to which Flask blueprints can be attached to.

## Configuration Variables

TBA

## Config Environment Variables

Flask Core accepts some configuration through environment variables.

#### FLAG_IDS

**Required**

Comma seperated list of a id for every flag on this site, these ids can then be used with `current_app.gen_flag(zid,flag_id)` to generate a actual flag. The id is just used so you can generate the same flag in multiple places and also so the `/core/checker` site works. 

#### FLAG_WRAP

**Required**

This is what generated flags are wrapped in, i.e if you set `FLAG_WRAP` to `BREAK1` then all flags will be in the format `BREAK1{abc...}`

#### FLAG_SECRET

**Required**

This is the secret key which flask will use to generate flags via the `current_app.gen_flag(zid,flag_id)`

#### DB_CONNECTION_STRING

**Required**

URI used to connect to a database.

Example:

```
postgres://root:root@localhost/test
``` 

#### FLASK_CORE_CONFIG

*Default: None*

When pointed to a valid pyconf file, this sets the contained options within Flask and Flask Core.

Example pyconf:

```python
THEME = "flatly"
TITLE = "A Title"
```

#### FLASK_CORE_ENABLE_AUTH

*Default: True*

Enforces user authentication.

#### FLASK_CORE_ENABLE_ISOLATION

*Default: True*

Isolates each user's database connection. Depends on user's authentication to function.

#### FLASK_CORE_AUTO_GENERATED_FLAGS

*Default: True*

Greps for flags in responses and replaces them with a user specific auto generated flag. Relies on auth. 

## Flag Generation

If you have auto flag generation turned on just stats all the flag_ids in the enviornment variable then you can either do 

```
current_app.gen_flag(zid,flag_id)
```

to generate a flag or actually just put the string

```
FLAG{_flagid}
```

in any response and it'll get auto grepped out and replaced with a actual flag. 

i.e 

```
FLAG_IDS=xss,csrf
```

chuck in the response 

```
FLAG{_xss}
```

and it'll get replaced :)
# Flask Core

This is a reusable core used to back COMP6443 applications.

## Overview

Flask Core is intended to be an installable Pip package to which Flask blueprints can be attached to.

## Configuration Variables

TBA

## Config Environment Variables

Flask Core accepts some configuration through environment variables.

#### FLAG
#### FLAG_SECRET
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

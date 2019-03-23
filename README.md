# Flask Core

This is a reusable core used to back COMP6443 applications.

## Overview

Flask Core is intended to be an installable Pip package to which Flask blueprints can be attached to.

## Config Environment Variables 

#### FLASK_CORE_ENABLE_AUTH

*Default: True*

Enforces user authentication.

#### FLASK_CORE_ENABLE_ISOLATION

*Default: True*

Isolates each user's database connection. Depends on user's authentication to function.

```
# Flask Core

This is a reusable core used to back COMP6443 applications.

## Overview

Flask Core is intended to be an installable Pip package to which Flask blueprints can be attached to.

## Config Enviornment Variables 

#### FLASK_CORE_ENABLE_AUTH
_defaults to True_

makes all users sign in to cse before proceeding

#### FLASK_CORE_ISOLATION_ENABLED
_defauls to True_

every user gets a isolated db, relies on FLASK_CORE_ENABLE_AUTH so is set to false if FLASK_CORE_ENABLE_AUTH is false.

```
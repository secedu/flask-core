#!/bin/bash
bumpversion minor
git push --tags
git push
make dist-clean
make dist
make twine
# make sure you are in the pipenv before running this

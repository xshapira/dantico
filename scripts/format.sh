#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ./dantico ./tests --exclude=__init__.py
black ./dantico ./tests
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --thirdparty dantico ./dantico ./tests

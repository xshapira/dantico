#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ./pydantic_django ./tests --exclude=__init__.py
black ./pydantic_django ./tests
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --thirdparty pydantic_django ./pydantic_django ./tests

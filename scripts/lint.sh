#!/usr/bin/env bash

set -e
set -x

mypy pydantic_django
black pydantic_django tests --check
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --check-only --thirdparty pydantic_django pydantic_django tests

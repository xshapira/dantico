#!/usr/bin/env bash

set -e
set -x

bash ./scripts/lint.sh
pytest tests
pytest --cov=dantico --cov=tests --cov-report=term-missing:skip-covered --cov-report=xml tests ${@}

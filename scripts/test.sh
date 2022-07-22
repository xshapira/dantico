#!/usr/bin/env bash

set -e
set -x

bash ./scripts/lint.sh
pytest tests

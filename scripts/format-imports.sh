#!/bin/sh -e
set -x

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports --thirdparty dantico ./dantico ./tests
sh ./scripts/format.sh

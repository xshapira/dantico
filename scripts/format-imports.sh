#!/bin/sh -e
set -x

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports --thirdparty pydantic_django ./pydantic_django ./tests
sh ./scripts/format.sh

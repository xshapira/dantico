.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Removing cached python compiled files
	find . -name \*pyc  | xargs  rm -fv
	find . -name \*pyo | xargs  rm -fv
	find . -name \*~  | xargs  rm -fv
	find . -name __pycache__  | xargs  rm -rfv

install: ## Install dependencies
	flit install --deps develop --symlink

lint: ## Run code linters
	make clean
	black --check pydantic_django tests
	isort --check pydantic_django tests
	flake8 pydantic_django tests
	mypy pydantic_django

fmt format: ## Run code formatters
	make clean
	black pydantic_django tests
	isort pydantic_django tests

test: ## Run tests
	make clean
	pytest .

test-cov: ## Run tests with coverage
	make clean
	pytest --cov=pydantic_django --cov-report term-missing tests

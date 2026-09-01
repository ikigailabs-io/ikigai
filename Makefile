# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

# Functions
define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

define check.branch
	@git branch --list | grep -q --fixed-strings '* development' || (echo "Error: Not on development branch"; exit 1)
endef

TOOL_OPEN := $(shell command -v open xdg-open | head -n1 || :)

TAG ?=
DEV ?= "--dev"
GH_NEW_RELEASE_URL := 'https://github.com/ikigailabs-io/ikigai/releases/new'

# Targets
help:
	@echo "--------------------------------------------------------------------"
	@echo "Options:"
	@echo ""
	$(call find.functions)
	@echo "--------------------------------------------------------------------"

.PHONY: all
all:			## Default make command (same as help)
all: help

.PHONY: build
build:			## Build the library
build: .init
	hatch build

.PHONY: test
test: 			## Run tests
test: .init
	hatch test $(ARGS)

.PHONY: format
format:			## Run formatter
format: .init
	hatch fmt

.PHONY: check
check:			## Run Linter and Type-Checker
check: .init
	hatch run check

.PHONY: bump
bump:           ## Bump the version string
bump: .init
ifdef TAG
	@./scripts/bump_version.py $(DEV) --part $(TAG)
else
	@./scripts/bump_version.py $(DEV)
endif
	@git add src/ikigai/__about__.py
	git commit -m "Bump version to v$$(hatch version)"
	git push

.PHONY: tag
tag:			## Create a new tag
tag: .init
	git tag "pcl-v$$(hatch version)"
	@echo "Created tag pcl-v$$(hatch version)\nPushing..."
	git push origin "pcl-v$$(hatch version)"

.PHONY: clean
clean:			## Clean the workspace
clean:
	rm test-env.toml .init || true

.init: Makefile
	@echo "Running checks..."
	@hatch --version > /dev/null || (echo "Please install hatch following the instructions in CONTRIBUTING.md" && exit 1)
# 	@pre-commit --version > /dev/null || (echo "Please install pre-commit by following the instructions in CONTRIBUTING.md" && exit 1)
# 	@pre-commit install > /dev/null
# 	@pre-commit run --all-files
# 	@[ -f "./test-env.toml" ] || (echo "Please follow instructions in CONTRIBUTING.md to setup test-env.toml file" && exit 1)
	@touch .init

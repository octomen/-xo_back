.PHONY: install test up

COMPORE=docker-compose -f docker/docker-compose.yaml
RUN_COMMAND=${COMPORE} run xo poetry run

test:
	${RUN_COMMAND} pytest

flake8:
	${RUN_COMMAND} flake8

checks: flake8 test

up:
	${COMPORE} up --build

build:
	${COMPORE} build

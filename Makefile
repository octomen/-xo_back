.PHONY: install test up

POETRY_RUN=poetry run

install:
	${POETRY_RUN} install

test:
	${POETRY_RUN} pytest -sv tests/

up:
	${POETRY_RUN} uvicorn --host 0.0.0.0 --port 8000 api.app:app

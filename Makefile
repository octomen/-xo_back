.PHONY: install test up

POETRY_RUN=venv/bin/poetry run

install:
	${RM} -R venv
	python3 -m venv venv
	venv/bin/pip install poetry
	venv/bin/poetry install

test:
	${POETRY_RUN} pytest tests/

up:
	${POETRY_RUN} uvicorn api.routers.game_router:app

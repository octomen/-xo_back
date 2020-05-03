FROM python:3.8-slim

WORKDIR app

RUN pip install poetry

ADD poetry.lock poetry.lock
ADD pyproject.toml pyproject.toml

RUN poetry install

ADD api api
ADD tests tests
ADD .flake8 .
ADD pytest.ini .

ENV PORT 8000
EXPOSE $PORT

CMD poetry run uvicorn --host 0.0.0.0 --port $PORT api.app:app
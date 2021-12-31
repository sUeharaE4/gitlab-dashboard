FROM python:3.9-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /work

ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
RUN cd /usr/local/bin && ln -s /opt/poetry/bin/poetry

COPY pyproject.toml* poetry.lock* ./
RUN poetry config virtualenvs.in-project false
RUN poetry install --no-dev

COPY .app_prop* ./

ENTRYPOINT ["poetry", "run", "task", "start"]
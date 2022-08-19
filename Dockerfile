# TODO: https://snyk.io/blog/best-practices-containerizing-python-docker/
LABEL AUTHOR="Proyecto Nutria <contact@proyectonutria.com>"

FROM python:3.10-slim

ENV POETRY_VERSION=1.1.14
# -m makes sure that you're using the pip tied to the active Python executable
RUN python3.10 -m pip install poetry==$POETRY_VERSION

WORKDIR /otter_welcome_buddy

# copy requirement files to ensure they will be cached
COPY poetry.lock pyproject.toml ./
# $HOME may changed by runtimes, virtual env solves reproducibility issues 
RUN poetry config virtualenvs.in-project true --local
RUN poetry install --no-dev

COPY . .
CMD [ "poetry", "run", "python", "otter_welcome_buddy" ]

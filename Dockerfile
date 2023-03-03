# TODO: https://snyk.io/blog/best-practices-containerizing-python-docker/
FROM python:3.10-slim
LABEL AUTHOR="Proyecto Nutria <contact@proyectonutria.com>"

ENV POETRY_VERSION=1.2
# -m makes sure that you're using the pip tied to the active Python executable
RUN python3.10 -m pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /root

# copy requirement files to ensure they will be cached
COPY poetry.lock pyproject.toml ./
# $HOME may changed by runtimes, virtual env solves reproducibility issues
RUN poetry config virtualenvs.in-project true --local \
 && poetry install --no-dev

COPY . .
CMD [ "poetry", "run", "python", "-m", "otter_welcome_buddy" ]

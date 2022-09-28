# Use an official Python runtime as a parent image
FROM python:3.10-alpine

# Adding backend directory to make absolute filepaths consistent across services
WORKDIR /app/core

# Install Python dependencies
RUN  \
    apk update && \
    apk upgrade && \
    apk add bash && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    apk --purge del .build-deps
    
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
# RUN source $HOME/.poetry/env
COPY pyproject.toml /app/core
RUN pip install poetry==1.1.13
RUN pip install psycopg2-binary
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Add the rest of the code
COPY . /app/core
COPY ./scripts/ /app/
# Make port 8000 available for the app
ENV PORT 8000
# EXPOSE 8000

RUN ["chmod", "+x", "/app/entrypoint.sh"]
RUN ["chmod", "+x", "/app/celery.sh"]

# ENTRYPOINT [ "/app/entrypoint.sh" ]
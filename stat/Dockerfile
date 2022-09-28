# Use an official Python runtime as a parent image
FROM python:3.10-alpine

WORKDIR /app/stat

RUN  \
    apk update && \
    apk upgrade && \
    apk add bash    

COPY pyproject.toml /app/stat
RUN pip install poetry==1.1.13
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY . /app/stat
COPY ./scripts/ /app/

ENV PORT 8000

RUN ["chmod", "+x", "/app/entrypoint.sh"]

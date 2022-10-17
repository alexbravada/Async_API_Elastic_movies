FROM python:3.10.2-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8106
WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY pyproject.toml ./
RUN pip install poetry==1.1 && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-dev

COPY . ./

CMD poetry run uvicorn --host=0.0.0.0 main:app --reload
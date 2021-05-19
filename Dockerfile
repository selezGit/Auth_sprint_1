FROM python:3.9.4-slim-buster


RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# set work directory
WORKDIR /usr/src/app


# install dependencies
RUN pip3 install --upgrade pip

COPY /src/requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt

# create directory for the app user
RUN mkdir -p /home/app
RUN mkdir -p /usr/src/tests

# create the app user
RUN addgroup --system app && adduser --system --no-create-home --group app

# copy project
COPY /src/async_api /usr/src/app

COPY /tests/ /usr/src/tests

RUN chmod +x /usr/src/app/entrypoint.sh

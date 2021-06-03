FROM python:3.9.4-slim-buster

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/gRPC

# install dependencies
RUN pip3 install --upgrade pip

COPY /requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt

# copy project
COPY . /usr/src/gRPC

EXPOSE 50051

ENTRYPOINT [ "python", "main.py" ]
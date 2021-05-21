FROM python:3.9.4-slim-buster

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/grpc

# install dependencies
RUN pip3 install --upgrade pip

COPY /src/grpc/requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt
# copy project
COPY /src/grpc /usr/src/grpc


ENTRYPOINT [ "python", "script.py" ]
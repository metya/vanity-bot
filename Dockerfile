FROM python:alpine

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on
ARG API_TOKEN
ENV API_TOKEN=$API_TOKEN

RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev curl
RUN apk add --no-cache git git-lfs

WORKDIR /app
ADD requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps

ADD . /app

# EXPOSE 8081

ENTRYPOINT [ "python", "vanitybot.py" ]
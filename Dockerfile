FROM python:alpine

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on
ARG API_TOKEN

WORKDIR /app
ADD prod-requirements.txt /app

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN pip install --no-cache-dir -r prod-requirements.txt
RUN apk del .build-deps

ADD . /app
RUN echo API_TOKEN=$API_TOKEN > config.py

# EXPOSE 8081

ENTRYPOINT [ "python", "vanitybot.py" ]
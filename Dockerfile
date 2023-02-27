FROM python:alpine

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on
ARG API_TOKEN
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=$GITHUB_TOKEN
ENV API_TOKEN=$API_TOKEN

RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev curl
RUN apk add --no-cache git git-lfs expect

WORKDIR /app
ADD requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps

# RUN echo "0 0 * * 1 /bin/sh /app/backup_db.sh" >> /var/spool/cron/crontabs/root
RUN echo "* * * * * /bin/sh /app/backup_db.sh" > /var/spool/cron/crontabs/root

RUN git config --global user.name "metya"
RUN git config --global user.email "metya.tm@gmail.com"

ADD . /app

ENTRYPOINT crond -f -l 0 && python vanitybot.py
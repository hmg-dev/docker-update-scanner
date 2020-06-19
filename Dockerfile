FROM python:3.8-alpine

RUN apk update && \
    apk add git bash openssl curl tzdata && \
    cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime

RUN mkdir -p /data/DUS && \
    mkdir -p /data/app

COPY dus /data/app/dus
COPY git-passwd-helper.sh /data/app/
COPY requirements.txt /data/app/

WORKDIR /data/app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1

CMD [ "python", "-m", "dus.app" ]

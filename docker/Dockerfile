FROM python:3.9-alpine

LABEL maintainer="Robert Kaussow <mail@thegeeklab.de>" \
    org.label-schema.name="ansible-later" \
    org.label-schema.vcs-url="https://github.com/thegeeklab/ansible-later" \
    org.label-schema.vendor="Robert Kaussow" \
    org.label-schema.schema-version="1.0"

ENV PY_COLORS=1

ADD dist/ansible_later-*.whl /

RUN apk --update add --virtual .build-deps build-base libffi-dev libressl-dev && \
    apk --update add git && \
    pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir ansible_later-*.whl && \
    apk del .build-deps && \
    rm -f ansible_later-*.whl && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache/

USER root
CMD []
ENTRYPOINT ["/usr/local/bin/ansible-later"]

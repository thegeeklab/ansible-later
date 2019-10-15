FROM python:3.7-alpine

LABEL maintainer="Robert Kaussow <mail@geeklabor.de>" \
    org.label-schema.name="ansible-later" \
    org.label-schema.vcs-url="https://github.com/xoxys/ansible-later" \
    org.label-schema.vendor="Robert Kaussow" \
    org.label-schema.schema-version="1.0"

ADD dist/ansible_later-*.whl /

RUN apk --update add --virtual .build-deps build-base libffi-dev libressl-dev pip && \
    pip install --upgrade --no-cache-dir git && \
    pip install --no-cache-dir --find-links=. ansible-later && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache/  && \
    rm -f ansible_later-*.whl

USER root
CMD []
ENTRYPOINT ["/usr/local/bin/ansible-later"]

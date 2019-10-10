FROM python:3.7-alpine

LABEL maintainer="Robert Kaussow <mail@geeklabor.de>" \
    org.label-schema.name="ansible-later" \
    org.label-schema.vcs-url="https://github.com/xoxys/ansible-later" \
    org.label-schema.vendor="Robert Kaussow" \
    org.label-schema.schema-version="1.0"

ADD dist/ansible_later-*.whl /

RUN \
    apk update --no-cache && \
    rm -rf /var/cache/apk/* && \
    pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir --find-links=. ansible-later && \
    rm -f ansible_later-*.whl && \
    rm -rf /root/.cache/

USER root
CMD []
ENTRYPOINT ["/usr/local/bin/ansible-later"]

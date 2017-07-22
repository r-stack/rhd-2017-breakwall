FROM httpd:2.4-alpine

# Install required softwares (curl, jq, AWS CLI)
RUN set -o errexit -o nounset \
    && apk add --no-cache curl openssl python3 jq \
    && curl -fsSkL "‌https://bootstrap.pypa.io/get-pip.py" | python3 - \
    && pip3 install awscli

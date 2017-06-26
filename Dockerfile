FROM python:3.6.1-alpine

RUN apk add --no-cache mariadb-dev g++ && \
    pip install --no-cache-dir mysqlclient && \
    apk del g++ mariadb-dev && \
    apk add --no-cache mariadb-client-libs

CMD ["ash"]
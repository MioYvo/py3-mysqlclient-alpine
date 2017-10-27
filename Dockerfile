FROM python:3.6.1-alpine
COPY . /mysql-parser/
RUN apk add --no-cache mariadb-dev g++ && \
    pip install --no-cache-dir -r /mysql-parser/requirements.txt && \
    apk del g++ mariadb-dev && \
    apk add --no-cache mariadb-client-libs

WORKDIR /mysql-parser/parser
CMD ["python", "run_server.py"]
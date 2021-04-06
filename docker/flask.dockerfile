FROM python:3.6-slim

ADD src/flask_server /flask_server

WORKDIR /flask_server

ADD requirements.txt /flask_server

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/flak_server

ENTRYPOINT ["/bin/bash", "-c", "flask run --host=0.0.0.0"]
FROM python:3.7

RUN apt-get update && apt-get install -y python3-dev supervisor nginx  \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /project/requirements.txt
RUN pip install -r /project/requirements.txt

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY nginx/supervisord.ini /etc/supervisor/conf.d/supervisord.ini

COPY app/ /project/app


COPY spec/ /project/spec

COPY test/ /project/test

WORKDIR /project

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]
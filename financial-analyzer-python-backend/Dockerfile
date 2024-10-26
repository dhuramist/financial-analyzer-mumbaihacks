FROM python:3.8-slim
COPY . /srv/flask_app
WORKDIR /srv/flask_app
RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential libpoppler-cpp-dev pkg-config python-dev


RUN pip install -r requirements.txt --src /usr/local/src
RUN mkdir logs
COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh
CMD ["./start.sh"]


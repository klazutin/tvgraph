FROM mongo:latest
EXPOSE 80

RUN apt-get update && apt-get install -y python3 python3-virtualenv python3-lxml git nginx supervisor build-essential python3-dev
RUN git clone --recursive https://github.com/klazutin/tvgraph.git
RUN cd /tvgraph
WORKDIR /tvgraph
RUN python3 -m virtualenv -p python3 --system-site-packages ./venv/
RUN . ./venv/bin/activate; pip install -U -r conf/requirements.txt

RUN mkdir /mongo
RUN mongod --fork --syslog --dbpath /mongo/ && mongo < conf/mongo.js

RUN rm /etc/nginx/nginx.conf
COPY ./conf/nginx.conf /etc/nginx/
RUN rm /etc/nginx/sites-enabled/default
COPY ./conf/nginx-tvgraph.conf /etc/nginx/sites-enabled/
COPY ./conf/supervisord-tvgraph.conf /etc/supervisor/conf.d/

CMD supervisord -n

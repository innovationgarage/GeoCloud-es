FROM ubuntu:18.04

RUN echo 2

RUN apt update
RUN apt install -y python3 python3-pip

RUN pip3 install elasticsearch
RUN pip3 install elasticsearch_dsl
RUN pip3 install socket-tentacles

ADD server.sh /server.sh
ADD gpsd2es.py /gpsd2es.py

CMD ["/bin/bash", "/server.sh"]

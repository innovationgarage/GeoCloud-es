# GeoCloud-es

A tool to upload a [GPSD JSON](https://gpsd.gitlab.io/gpsd/AIVDM.html)
feed received over a tcp connection into Elastic Search. Inserts
positional and non-positional messages in separate indexes, and
annotates positional messages with the latest type 5 message from the
same MMSI.

Usage:

    python gpsd2es.py config.json

## Docker

    docker build --tag geocloud-es .

    docker run \
      -p 1024:1024 \
      -e 'CONFIG={"es_host" : "192.168.0.1:9200", "connections": [{"handler": "source", "type": "listen", "address": "tcp:1024"}]}' \
      geocloud-es

#! /bin/bash

echo "$CONFIG" > config.json
geocloud-es config.json

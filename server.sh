#! /bin/bash

echo "$CONFIG" > config.json
python3 /gpsd2es.py config.json

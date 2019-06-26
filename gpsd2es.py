import sys
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch import helpers
import socket_tentacles
import json

def is_positional(msg):
    if ('lon' in msg.keys()) and ('lat' in msg.keys()):
        return True
    else:
        return False

def find_vessel(mmsi, client, vessels_index):
    # find the latest type5
    s = Search(using=client, index=vessels_index)\
        .query("match", mmsi=mmsi)\
        .filter("term", type=5)\
        .sort({"timestamp" : {"order":"desc"}})
    response = s.execute()
    last_type5_msg = response[0].to_dict()
    return last_type5_msg

def add_to_ES(msg, client, index):
    try:
        return client.index(index=index, body=msg)
    except Exception as e:
        print(msg, e)
    
def make_ES_doc(msg, client, vessels_index, positions_index):
    if is_positional(msg):
        try:
            last_type5_msg = find_vessel(msg['mmsi'], client, vessels_index)
        except:
            last_type5_msg = {}
        msg['last_type5'] = last_type5_msg
        index = positions_index
        msg['location'] = {'coordinates': [msg['lon'], msg['lat']],  'type': 'point'}
    else:
        index = vessels_index
    add_to_ES(msg, client, index)

class ReceiveHandler(socket_tentacles.ReceiveHandler):
    def handle(self):
        client = Elasticsearch(["http://{}".format(es_host)])        
        #FIXME! add a check for indices vs time, if index does not exist, add a new one
        #client.indices.create(index=index)
        vessels_index = 'geocloud-vessels-2019'
        positions_index = 'geocloud-positions-2019.06'
        for line in self.file:
            msg = json.loads(line)
            make_ES_doc(msg, client, vessels_index, positions_index)
            
if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        config = json.load(f)
        
    es_host = config['es_host']
    socket_tentacles.run(config, {"source": ReceiveHandler})

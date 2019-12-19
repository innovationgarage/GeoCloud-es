import sys
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch import helpers
import socket_tentacles
import json
from datetime import datetime
import dateutil.parser

es_host = None
config = None

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
        return client.index(index=index, body=msg, id=msg['mmsi'])
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
        msg['location'] = {'lon': [msg['lon'], 'lat':msg['lat']]}
    else:
        index = vessels_index
    add_to_ES(msg, client, index)

def zeropad(n):
    if n<10:
        return "0"+str(n)
    else:
        return str(n)
    
class ReceiveHandler(socket_tentacles.ReceiveHandler):
    def handle(self):
        client = Elasticsearch(["http://{}".format(es_host)])
        #FIXME! add a check for indices vs time, if index does not exist, add a new one
        #client.indices.create(index=index)
        for line in self.file:
            print(type(line))
            msg = json.loads(line)
            msg_ts = dateutil.parser.parse(msg['timestamp'])
            print(msg_ts.year, zeropad(msg_ts.month))
            vessels_index = 'geocloud-vs-'+str(msg_ts.year)
            if msg['class']=='AIS':
                positions_index = 'geocloud-ais-'+str(msg_ts.year)+'.'+zeropad(msg_ts.month)
            elif msg['class']=='TS':
                positions_index = 'geocloud-ts-'+str(msg_ts.year)+'.'+zeropad(msg_ts.month)

            if config['vessels_index'] != vessels_index:
                if not client.indices.exists(index=vessels_index):
                    client.indices.create(index=vessels_index, body=config['vessels_mapping'])
            else:
                config['vessels_index'] = vessels_index
                
            if config['positions_index'] != positions_index:
                if not client.indices.exists(index=positions_index):
                    client.indices.create(index=positions_index, body=config['positions_mapping'])
            else:
                config['positions_index'] = positions_index

            make_ES_doc(msg, client, vessels_index, positions_index)

def main(*arg, **kw):
    global config
    global es_host
    
    with open(sys.argv[1]) as f:
        config = json.load(f)
        
    es_host = config['es_host']
    socket_tentacles.run(config, {"source": ReceiveHandler})
            
if __name__ == "__main__":
    main()

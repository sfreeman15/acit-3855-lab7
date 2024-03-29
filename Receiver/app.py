import connexion
from connexion import NoContent
import json
import datetime
import os.path
import requests
import uuid
from threading import Lock
import yaml
import logging
import logging.config
from pykafka import KafkaClient


MAX_EVENTS= 5
EVENT_FILE = "events.json"




    
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')


def purchase(body):

    trace_id = uuid.uuid4()
    body["trace_id"] = str(trace_id)
    print(body)
    logger.info("Received event Purchase request with a trace ID of %s %s", body["trace_id"], body )
    headers =  { "content-type": "application/json" }
    # response = requests.post(app_config["eventstore1"]["url"], json=body, headers=headers)

    client = KafkaClient(hosts='acit-3855-kafka.westus3.cloudapp.azure.com:9092')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "purchase",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
   
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Returned event Purchase response (Id: %s) with status %s",body["trace_id"], 201)
    return NoContent, 201 



def upload_ticket(body):

    trace_id = uuid.uuid4()
    body["trace_id"] = str(trace_id)
    print(body)
    logger.info("Received event upload request with a trace ID of %s %s", body["trace_id"], body )
    headers =  { "content-type": "application/json" }
    # response = requests.post(app_config["eventstore1"]["url"], json=body, headers=headers)

    client = KafkaClient(hosts='acit-3855-kafka.westus3.cloudapp.azure.com:9092')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = { "type": "upload",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
   
    producer.produce(msg_str.encode('utf-8'))
    logger.info("Returned event upload response (Id: %s) with status %s",body["trace_id"], 201)
    return NoContent, 201 


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)
     

if __name__ == "__main__":
    app.run(port=8080)
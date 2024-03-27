import connexion
from connexion import NoContent
import datetime
import requests
import yaml
from threading import Lock
import logging
import logging.config
import uuid
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from flask_cors import CORS, cross_origin
import os


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)





def get_purchases(index):
    """ Get ticket purchase in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving ticket purchaes  at index %d" % index)
    current_index = 0
    try:
        count=0
        for msg in consumer:
            # msg = json.loads(msg.value.decode('utf-8'))
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # print(type(msg))
            # print(msg['type'])
            
            if msg['type']=='purchase':
                # print("here")
                # msg_str = msg.value.decode('utf-8')
                if count==index:
                    return msg['payload'], 200
        
                count+=1
            # print(type(msg))
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find upload reading at index %d" % index)
    return {"message": "Not Found"}, 404

def get_uploads(index):
    """ Get ticket upload in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving ticket upload at index %d" % index)
    current_index = 0
    try:
        count=0
        for msg in consumer:
            # msg = json.loads(msg.value.decode('utf-8'))
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # print(type(msg))
            # print(msg['type'])
            
            if msg['type']=='upload':
                # print("here")
                # msg_str = msg.value.decode('utf-8')
                if count==index:
                    return msg['payload'], 200
        
                count+=1
            # print(type(msg))
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find upload reading at index %d" % index)
    return {"message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(port=8110, host="0.0.0.0")

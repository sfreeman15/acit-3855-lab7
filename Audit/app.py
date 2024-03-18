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



with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

    
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)




logger = logging.getLogger('basicLogger')
    



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
    logger.info("Retrieving BP at index %d" % index)
    current_index = 0
    try:
        for msg in consumer:
            # Other code...
            if current_index == index:
                current_index += 1  # Move the increment here
                return msg, 200
                
            current_index += 1

            if current_index > index:
                break

    # Find the event at the index you want and
    # return code 200
    # i.e., return event, 200
    except:
        logger.error("No more messages found")
        logger.error("Could not find BP at index %d" % index)
    return { "message": "Not Found"}, 404

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
        for msg in consumer:
            # Other code...
            if current_index == index:
                current_index += 1  # Move the increment here
                return msg, 200
                
            current_index += 1

            if current_index > index:
                break

    # Find the event at the index you want and
    # return code 200
    # i.e., return event, 200
    except:
        logger.error("No more messages found")
        logger.error("Could not find ticket upload at index %d" % index)
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(port=8110, host="0.0.0.0")

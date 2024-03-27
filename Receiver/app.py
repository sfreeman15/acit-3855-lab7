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
import time
import os

MAX_EVENTS= 5
EVENT_FILE = "events.json"



    
# Create a consume on a consumer group, that only reads new messages
# (uncommitted messages) when the service re-starts (i.e., it doesn't
# read all the old messages from the history in the message queue).
# This is blocking - it will wait for a new message
current_retry_count = 0 


    
import os
import yaml
import logging
import logging.config

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/receiver/app_conf.yml"
    log_conf_file = "/config/receiver/log_conf.yml"
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


sleepy_time = app_config['sleepy_time']["sleep_in_sec"]


while current_retry_count < app_config["retries"]['retry_count']:
    logger.info(f"Connecting to Kafka. Current retry count: {current_retry_count}")
    try:    
        client = KafkaClient(hosts='acit-3855-kafka.westus3.cloudapp.azure.com:9092')
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        producer = topic.get_sync_producer()

        logger.info("Connected!")
        break #yahoo 
    except:
        logger.error("Connection failed")
        time.sleep(sleepy_time)
        current_retry_count += 1
           
        

def producer2(current_retry_count):
    while current_retry_count < app_config["retries"]['retry_count']:
        logger.info(f"Connecting to Kafka. Current retry count: {current_retry_count}")
        try:    
            logger.info("Connected!")
            hostname = "%s:%d" % (app_config["event_log"]["hostname"],app_config["event_log"]["port"])
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["event_log"]["topic"])]
            producer2 = topic.get_sync_producer()
            msg = { "message_code": "0001", 
                    "message": "Ready to receive messages on RESTful API"}
            msg_str = json.dumps(msg)
            logger.info(msg_str)

            producer2.produce(msg_str.encode('utf-8'))
            break
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            time.sleep(sleepy_time)
            current_retry_count += 1
           
    


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
    producer2(current_retry_count=current_retry_count)
    app.run(port=8080, host="0.0.0.0")
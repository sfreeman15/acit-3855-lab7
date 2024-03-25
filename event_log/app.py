import connexion
from connexion import NoContent
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from event_logs import EventLogs
import datetime
import requests
import yaml
from threading import Lock
import logging
import logging.config
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
import json
from flask_cors import CORS, cross_origin
from pytz import timezone
from pykafka import KafkaClient
from pykafka.common import OffsetType

import logging


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')


# Configure logging

DB_ENGINE = create_engine("sqlite:///event_log.sqlite")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)



def event_stats():
    logger.info("Request has started")
    session = DB_SESSION()
    pst = timezone('America/Vancouver')


    statistics = session.query(EventLogs.message_code).all()
    logger.info(statistics)
    # last_updated_pst = statistics.date_time.astimezone(pst)
 
    stat_dict = {
        "0001": 0,
        "0002": 0,
        "0003": 0,
        "0004": 0
    }

    for code_tuple in statistics:
        code = code_tuple[0]  # Extracting the message code from the tuple
        if code == "0001":
            stat_dict["0001"] += 1
        elif code == "0002": 
            stat_dict["0002"] += 1
        elif code == "0003": 
            stat_dict["0003"] += 1
        elif code == "0004": 
            stat_dict["0004"] += 1


    session.close()
    logger.info("Request has completed")
    return stat_dict, 200


def process_messages():
    logger.debug("Start of process_messages function")
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    pst = timezone('America/Vancouver')
    client = KafkaClient(hosts=hostname)

    topic = client.topics[str.encode(app_config["event_log"]["topic"])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)
    
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        
        # Extract message data from the message received
        message_code = msg.get("message_code")
        message = msg.get("message")
        
        # Here you can perform any processing required with the message data
        
        # Example: Storing the message in the database
        session = DB_SESSION()
        try:
            event_log = EventLogs(
                message_code=message_code,
                message=message,
                date_time=datetime.now()  # You may adjust this based on your requirements
            )
            session.add(event_log)
            session.commit()
            logger.info("Message processing completed")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            session.rollback()
        finally:
            session.close()

        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)



if __name__ == "__main__":  
# run our standalone gevent server
    app.run(port=8120, host="0.0.0.0")


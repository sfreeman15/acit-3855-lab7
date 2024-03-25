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
    logger.info("Request has started")
    hostname = "%s:%d" % (app_config["event_log"]["hostname"], app_config["event_log"]["port"])

    pst = timezone('America/Vancouver')
    client = KafkaClient(hosts=hostname)

    topic = client.topics[str.encode(app_config["event_log"]["topic"])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)
    
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        session = DB_SESSION()
        event_log = EventLogs(payload["event_id"],
                              payload["message"],
                              payload["message_code"],
                              payload["date_time"])
        if event_log:
            session.add(event_log)

        logger.info("Message processing completed")

        consumer.commit_offsets()
        session.commit()  # Commit any pending transactions
        session.close()   # Close the session to release resources

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)



if __name__ == "__main__":  
# run our standalone gevent server
    app.run(port=8120, host="0.0.0.0")


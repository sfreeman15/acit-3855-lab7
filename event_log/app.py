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
import sqlite3
import os.path


import logging


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

database_path = "/app/event_log.sqlite"  # Update this with the correct path


# Check if the database file exists
if not os.path.exists(database_path):
    # If the file doesn't exist, create the database and table
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE event_log (
            event_id INTEGER PRIMARY KEY ASC,
            message TEXT NOT NULL,
            message_code TEXT NOT NULL,
            date_time VARCHAR(100) NOT NULL
        )
    ''')

    conn.commit()
    conn.close()



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

    # Begin processing messages
    for message in consumer:
        try:
            # Decode the message and parse JSON
            msg = json.loads(message.value.decode('utf-8'))
        
            # Access the message fields
            message_code = msg["message_code"]
            message_content = msg["message"]

            # Log the message
            logger.info("Message: %s" % msg)

            # Process the message
            session = DB_SESSION()
            event_log = EventLogs(message=message_content, message_code=message_code)
            session.add(event_log)
            session.commit()  # Commit any pending transactions
            session.close()   # Close the session to release resources

            # Commit offsets after processing a message
            consumer.commit_offsets()

            logger.info("Message processing completed")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

# Call the function to start message processing
process_messages()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)



if __name__ == "__main__":  
# run our standalone gevent server
    app.run(port=8120, host="0.0.0.0")


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
import time
from threading import Thread


import logging


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')
logger.info(f'Connecting to DB.Hostname:"{app_config["datastore"]["filename"]}')

database_path = "/app/event_log.sqlite"  # Update this with the correct path

# Check if the database file exists
if not os.path.isfile(database_path):
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

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def process_messages():
    logger.info("Request has started")
    retries = app_config["retries"]["retry_count"]
    sleepy_time = app_config["sleepy_time"]["sleep_in_sec"]
    current_retry_count = 0  # Initialize the retry count
    while current_retry_count < retries:
        try:
            logger.info(f"Connecting to Kafka. Current retry count: {current_retry_count}")
            hostname = "%s:%d" % (app_config["event_log"]["hostname"], app_config["event_log"]["port"])
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["event_log"]["topic"])]
            consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)
            logger.info("Connected to Kafka!")
            break  # Exit the loop if connection successful
        except Exception as e:  # Catch specific exceptions for better error handling
            logger.error(f"Connection failed: {str(e)}")
            time.sleep(sleepy_time)
            current_retry_count += 1

    if current_retry_count >= retries:
        logger.error("Maximum retries reached. Exiting process_messages.")
        return
    logger.info("adding to database:")


    for msg in consumer:
        try:
            msg_str = msg.value.decode('utf-8')
            logger.debug(f"Raw message: {msg_str}")  # Log the raw message
            msg = json.loads(msg_str)
            logger.info(msg)
            msg_info = msg["message"]
            msg_code = msg["message_code"]

            session = DB_SESSION()

            date_time = datetime.datetime.now()        

            event_log = EventLogs(message=msg_info, message_code=msg_code, date_time=date_time)
        
            session.add(event_log)

            logger.debug("Message processing completed")

            session.commit()  # Commit any pending transactions
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            session.rollback()  # Rollback transaction in case of error
        finally:
            session.close()   # Close the session to release resources
            consumer.commit_offsets()



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





app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

CORS(app.app)
app.app.config["CORS_HEADERS"] = "Content-Type"

if __name__ == "__main__":  
# run our standalone gevent server
    t1 = Thread(target=process_messages)
    
    t1.setDaemon(True)

    t1.start()

    app.run(host="0.0.0.0",port=8120)


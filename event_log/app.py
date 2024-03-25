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
from sqlalchemy import func
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

    statistics = session.query(EventLogs).all()
    logger.info(statistics)
    for event_log in statistics:
        print(event_log.message_code)  # Access the 'message_code' column
        print(event_log.message)      # Access the 'message' column
        print(event_log.created_at)   # Access the 'created_at' column

    # last_updated_pst = statistics.date_time.astimezone(pst)
 
    # Create an empty dictionary to store the counts
    stat_dict = {
        "0001": 0,
        "0002": 0,
        "0003": 0,
        "0004": 0
    }

    # Query to count occurrences of each message code
    message_code_counts = session.query(EventLogs.message_code, func.count(EventLogs.message_code)).group_by(EventLogs.message_code).all()

    # Update the counts in the dictionary
    for message_code, count in message_code_counts:
        stat_dict[message_code] = count

    session.close()
    logger.info("Request has completed")


    
    return stat_dict, 200


from datetime import datetime
from pytz import timezone
from pykafka.common import OffsetType

def process_messages():
    logger.info("Request has started")

    hostname = "%s:%d" % (app_config["event_log"]["hostname"], app_config["event_log"]["port"])
    client = KafkaClient(hosts=hostname)

    topic = client.topics[str.encode(app_config["event_log"]["topic"])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    for message in consumer:
        # Decode the message and parse JSON
        msg = json.loads(message.value.decode('utf-8'))
        
        # Access the message fields
        msg_code = msg.get("message_code")
        message_content = msg.get("message")

        if msg_code == "0001" and message_content:  # Check if it's the message you want to store
            try:
                # Open a session and add the event log to the database
                session = DB_SESSION()
                event_log = EventLogs(message_code=msg_code, message=message_content, created_at=datetime.now(timezone('America/Vancouver')))
                session.add(event_log)
                session.commit()  # Commit changes to the database
                session.close()
                logger.info("Message processed and stored successfully.")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                session.rollback()  # Rollback changes in case of an error

        consumer.commit_offsets()

    logger.info("Message processing completed.")


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)



if __name__ == "__main__":  
# run our standalone gevent server
    app.run(port=8120, host="0.0.0.0")


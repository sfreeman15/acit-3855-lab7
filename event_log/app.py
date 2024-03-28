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
from sqlalchemy import func






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



logger.info(f'Connecting to DB.Hostname:"{app_config["datastore"]["filename"]}')

database_path = "/app/data/event_log.sqlite"  # Update this with the correct path


DB_ENGINE = create_engine("sqlite:////data/event_log.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

database_path = "/app/data/event_log.sqlite"  # Update this with the correct path
def check_file_exists():
    current_time = datetime.datetime.now()
    try:
        # Check if the database file exists
        if not os.path.isfile(database_path):
            session = DB_SESSION()
            # Create the database table if it doesn't exist
            conn = sqlite3.connect('/data/event_log.sqlite')
            c = conn.cursor()

            c.execute('''
                CREATE TABLE stats (
                    id INTEGER PRIMARY KEY ASC,
                    num_tp_readings INTEGER NOT NULL,
                    max_tp_readings REAL,
                    num_tu_readings INTEGER NOT NULL,
                    max_tu_readings REAL,
                    last_updated VARCHAR(100) NOT NULL
                )
            ''')

            conn.commit()
            conn.close()

            # Insert default values into the table
            most_recent_statistic = Stats(
                num_tp_readings=0,
                max_tp_readings=0,
                num_tu_readings=0,
                max_tu_readings=0,
                last_updated=current_time
            ) 
            session.add(most_recent_statistic)
            session.commit()
            session.close()
            logger.info("No database file found. Created file and added default values.")
    except Exception as e:
        logger.error(f"Error creating database file and table structure: {e}")


check_file_exists()

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


    pst = timezone('America/Vancouver')



    for msg in consumer:
        try:
            msg_str = msg.value.decode('utf-8')
            logger.debug(f"Raw message: {msg_str}")  # Log the raw message
            message = json.loads(msg_str)

            
            og_message = message["message"]
            code =message["message_code"]
            


            session = DB_SESSION()

            date_time = datetime.datetime.now()        
            date_time =  date_time.astimezone(pst)
            event_log = EventLogs(message=og_message, message_code=code, date_time=date_time)
        
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
    try:
        session = DB_SESSION()
        pst = timezone('America/Vancouver')

        # Query and count occurrences of each message code
        statistics = session.query(EventLogs.message_code, func.count()).group_by(EventLogs.message_code).all()
        logger.info(statistics)

        # Initialize stat_dict
        stat_dict = {
            "0001": 0,
            "0002": 0,
            "0003": 0,
            "0004": 0
        }

        # Iterate over statistics and update stat_dict
        for code, count in statistics:
            # Ensure code is a string by converting it to str
            code = str(code)
            stat_dict[code] = count

        session.close()
        logger.info("Request has completed")
        return stat_dict, 200
    except Exception as e:
        logger.error(f"Error processing event stats: {e}")
        return {"error": "An error occurred while processing event stats"}, 500





app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config["CORS_HEADERS"] = "Content-Type"

app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)



if __name__ == "__main__":  
# run our standalone gevent server
    t1 = Thread(target=process_messages)
    
    t1.setDaemon(True)

    t1.start()

    app.run(host="0.0.0.0",port=8120)


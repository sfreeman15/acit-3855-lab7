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

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

import logging

# Configure logging
logging.basicConfig(filename='event_logger.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_ENGINE = create_engine("sqlite:///event_log.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)



def event_stats():
    logger.info("Request has started")

    session = DB_SESSION()
    pst = timezone('America/Vancouver')
    client = KafkaClient(hosts=hostname)

    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)


    for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info("Message: %s" % msg)
            payload = msg["payload"]
    session = DB_SESSION()

    event_log = EventLogs(payload["id"],
                          payload["message"],
                          payload["message_code"],
                          payload["date_time"])
    if event_log:
         session.add(event_log)
    
    session.commit()
    session.close()
        
    most_recent_statistic = session.query(Stats).order_by(Stats.id.desc()).first()
    last_updated_pst = most_recent_statistic.last_updated.astimezone(pst)
    if most_recent_statistic is None:
         logger.error("ERROR, NOTHING IN DATA IN TABLES")
         return "Statistics do not exist", 404
    # stats_dict = most_recent_statistic.json()
    pydict = {"num_tp_readings": most_recent_statistic.num_tp_readings,
              "num_tu_readings":most_recent_statistic.num_tu_readings,
              "max_tp_readings": most_recent_statistic.max_tp_readings,
              "max_tu_readings": most_recent_statistic.max_tu_readings,
              "last_updated": last_updated_pst.strftime('%Y-%m-%d %H:%M:%S %Z%z')}
    session.close()
    logger.info("Request has completed")
    return pydict, 200
    
import connexion
from connexion import NoContent
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from ticket_purchase import TicketPurchase
from ticket_upload  import TicketUpload
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




with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')

logger.info(f'Connecting to DB.Hostname:"{app_config["datastore"]["hostname"]}. Port: {app_config["datastore"]["port"]}')


Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

MAX_EVENTS= 5
EVENT_FILE = "events.json"



# def purchase(body):
  

#     session = DB_SESSION()
#     tp =  TicketPurchase(body['ticket_id'],
#                          body['concert_name'],  
#                          body["seat_number"],
#                          body["artist"],
#                          body['date'],
#                          body['venue'],
#                          body['price'],
#                          body['trace_id'])
#     session.add(tp)
#     session.commit()
#     session.close()
  
#     logger.debug("Stored Purchase request with a trace ID of %s", body["trace_id"])
#     return NoContent, 201


def get_purchases(start_timestamp, end_timestamp):
    """ Gets new ticket purchases between the start and end timestamps """
    session = DB_SESSION()
    
    
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

   
    results = session.query(TicketPurchase).filter( and_(TicketPurchase.date_created >= start_timestamp_datetime, TicketPurchase.date_created < end_timestamp_datetime))
    results_list = []

    for ticket in results:
        results_list.append(ticket.to_dict())
    
    session.close()
    logger.info("Query for ticket purchases after %s returns %d results" % (start_timestamp, len(results_list)))
    return results_list, 200




# def upload_ticket(body):
   

#     session = DB_SESSION()

#     tu = TicketUpload(body['ticket_id'],
#                    body['seller_name'],
#                    body['seat_number'],
#                    body["artist"],
#                    body['concert_name'],
#                    body['date'],
#                    body["venue"],
#                    body["price"],
#                    body['trace_id'])

    
#     session.add(tu)

#     session.commit()
#     session.close()
#     logger.debug("Stored Upload_ticket request with a trace ID of %s", body["trace_id"])
#     return NoContent, 201



def get_uploads(start_timestamp, end_timestamp):
    """ Gets new blood pressure readings between the start and end timestamps """
    session = DB_SESSION()  
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    results = session.query(TicketUpload).filter(and_(TicketUpload.date_created >= start_timestamp_datetime,TicketUpload.date_created < end_timestamp_datetime))
    results_list = []
    for reading in results:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for ticket upload readings after %s returns %d results" %(start_timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    logger.debug("Start of process_messages function")
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False,auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        logger.info(f'this is the message: {msg["type"]}')
        if msg["type"] == "purchase": # Change this to your event type
            logger.info(f'message type is purchase: {msg["type"]}')
            session = DB_SESSION()
            tp =  TicketPurchase(payload['ticket_id'],
                                payload['concert_name'],  
                                payload["seat_number"],
                                payload["artist"],
                                payload['date'],
                                payload['venue'],
                                payload['price'],
                                payload['trace_id'])
            session.add(tp)
            session.commit()
            session.close()
  
            logger.debug("Stored Purchase request with a trace ID of %s", payload["trace_id"])
            # Store the event1 (i.e., the payload) to the DB
        elif msg["type"] == "upload": # Change this to your event type
            logger.info(f' message type is upload: {msg["type"]}')
            session = DB_SESSION()
            tu = TicketUpload(payload['ticket_id'],
                   payload['seller_name'],
                   payload['seat_number'],
                   payload["artist"],
                   payload['concert_name'],
                   payload['date'],
                   payload["venue"],
                   payload["price"],
                   payload['trace_id'])

    
            session.add(tu)

            session.commit()
            session.close()
            logger.debug("Stored Upload_ticket request with a trace ID of %s", payload["trace_id"])
            
        # Store the event2 (i.e., the payload) to the DB
        # Commit the new message as being read
        consumer.commit_offsets()



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)
     

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    
    t1.daemon = True 

    t1.start()

    app.run(port=8090)

   
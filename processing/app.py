import connexion
from connexion import NoContent
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
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




with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///stats.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
 

def populate_stats():
    """ Periodically update stats """
    logger.info("Started Periodic Processing")
    time = datetime.datetime.now()
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    session = DB_SESSION()
    most_recent_statistic = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    #SOURCE: https://stackoverflow.com/questions/8551952/how-to-get-last-record
    
    
    default_values = {
            'num_tp_readings': 0,
            'num_tu_readings': 0,
            'max_tp_readings': 0,
            'max_tu_readings': 0,
            'last_updated': datetime.datetime.now()}    
  
    
    if most_recent_statistic is None:
        print("nothing")
        most_recent_statistic = Stats(
             num_tp_readings = 0,
             max_tp_readings = 0,
             num_tu_readings = 0,
             max_tu_readings = 0,
             last_updated= time

        )
        session.add(most_recent_statistic)
        print("added")
        session.commit()
       
        logger.info(f"Number of purchase events received: {default_values['num_tp_readings']}. Number of upload events received: {default_values['num_tu_readings']}")
        # stats = Stats(default_values['num_tp_readings'], default_values['num_tu_readings'], default_values["max_tp_readings"], default_values["max_tu_readings"], default_values["last_updated"])
        logger.debug(f'Updated Statistics Values - num_tp_readings:{default_values["num_tp_readings"]}, num_tu_readings: {default_values["num_tu_readings"]}max_tp_readings: {default_values["max_tp_readings"]}, max_tu_readings: {default_values["max_tu_readings"]}, last_updated: {default_values["last_updated"]}')
        

  
    last_hour_datetime = datetime.datetime.now()
    end_timestamp = last_hour_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    

   
    
    database_time = most_recent_statistic.last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    purchase_requests = requests.get(f'{app_config["eventstore"]["url"]}/sales/purchase?start_timestamp={database_time}&end_timestamp={end_timestamp}') #needs to include start_timestamp and end_timestamp
    upload_request = requests.get(f'{app_config["eventstore"]["url"]}/sales/upload?start_timestamp={database_time}&end_timestamp={end_timestamp}') #needs to include start_timestamp and end_timestamp
    purchase_data = purchase_requests.json()
    upload_data = upload_request.json()

    
    max_value_p = most_recent_statistic.max_tp_readings
    max_value_u = most_recent_statistic.max_tu_readings
    
   # # Check if the length of purchase_data exceeds the current maximum TP readings
   #  # and if the number of TP readings didn't increase
   #  if len(purchase_data) > max_value_p:
   #      # Update max_value_p with the new maximum TP readings
   #      max_value_p = len(purchase_data)
   #      # Update updated_purchase_val with the new maximum TP readings

   #  # Check if the length of upload_data exceeds the current maximum TU readings
   #  # and if the number of TU readings didn't increase
   #  if len(upload_data) > max_value_u:
   #      # Update max_value_u with the new maximum TU readings
   #      max_value_u = len(upload_data)
   #      # Update updated_upload_val with the new maximum TU readings

    for i in purchase_data:
         if max_value_p < i["price"]:
              max_value_p = i["price"]
    for j in upload_data:
         if max_value_u < j["price"]:
              max_value_u = j["price"]


    if most_recent_statistic:
        for index in range(len(purchase_data)):
                logger.debug(f'Purchase trace_id: {purchase_data[index]["trace_id"]}')
        for index in range(len(upload_data)):
                logger.debug(f'Upload trace_id: {upload_data[index]["trace_id"]}')
            
        # logger.debug(f'Updated Statistics Values - num_tp_readings: {most_recent_statistic.num_tp_readings}, num_tu_readings: {most_recent_statistic.num_tu_readings}, max_tp_readings: {most_recent_statistic.max_tp_readings}, max_tu_readings: {most_recent_statistic.max_tu_readings}, last_updated: {most_recent_statistic.last_updated}')


    logger.info("yes")
    # logger.info(f"{purchase_data.status_code}")
    

    logger.info(f"Number of purchase events received: {len(purchase_data)}. Number of upload events received: {len(upload_data)}")
    stats = Stats(num_tp_readings=most_recent_statistic.num_tp_readings + len(purchase_data), num_tu_readings=most_recent_statistic.num_tu_readings + len(upload_data), max_tp_readings=max_value_p, max_tu_readings=max_value_u, last_updated=last_hour_datetime)
    
    
    



    
    if stats:
         session.add(stats)
    
    session.commit()
    session.close()
    if purchase_data != None:
        print(f'purchase data: {purchase_data}')
    else:
        print("doesn't exist")
    print(purchase_requests.status_code)
    print(purchase_data)
    logger.info("Processing Period has ended.")
    



def init_scheduler():
    sched = BackgroundScheduler(daemon=True, timezone=timezone('America/Los_Angeles'))
    sched.add_job(populate_stats,
    'interval',
    seconds=app_config['scheduler']['period_sec'])
    sched.start()

def get_stats():
    logger.info("Request has started")
    session = DB_SESSION()
    pst = timezone('America/Vancouver')

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
              "last_updated": last_updated_pst.strftime('%Y-%m-%d ^H:%M:%S %Z%z')}
    session.close()
    logger.info("Request has completed")
    return pydict, 200
    

    


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'



if __name__ == "__main__":  
# run our standalone gevent server
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")


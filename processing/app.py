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
    
    num_tp_readings_updated = most_recent_statistic.num_tp_readings
    num_tu_readings_updated = most_recent_statistic.num_tu_readings
    max_tp_readings_updated = most_recent_statistic.max_tp_readings
    max_tu_readings_updated = most_recent_statistic.max_tu_readings
    
    database_time = most_recent_statistic.last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    purchase_requests = requests.get(f'{app_config["eventstore"]["url"]}/sales/purchase?start_timestamp={database_time}&end_timestamp={end_timestamp}') #needs to include start_timestamp and end_timestamp
    upload_request = requests.get(f'{app_config["eventstore"]["url"]}/sales/upload?start_timestamp={database_time}&end_timestamp={end_timestamp}') #needs to include start_timestamp and end_timestamp
    purchase_data = purchase_requests.json()
    upload_data = upload_request.json()

    
    if purchase_requests.status_code != 200:
        logger.error(f"Error, purchase request returned status code {purchase_requests.status_code}")

     updated_purchase_val = most_recent_statistic.max_tp_readings 
    updated_upload_val = most_recent_statistic.max_tu_readings 

    if most_recent_statistic:
        max_value_p = most_recent_statistic.max_tp_readings
        max_value_u = most_recent_statistic.max_tu_readings

    if len(purchase_data) > max_value_p and most_recent_statistic.num_tp_readings < len(purchase_data):
        max_value_p = len(purchase_data)
        updated_purchase_val = max_value_p

    if len(upload_data) > max_value_u and most_recent_statistic.num_tu_readings < len(upload_data):
        max_value_u = len(upload_data)
        updated_upload_val = max_value_u

    logger.info(f"Number of purchase events received: {len(purchase_data)}. Number of upload events received: {len(upload_data)}")
    stats = Stats(num_tp_readings=len(purchase_data), num_tu_readings=len(upload_data), max_tp_readings=max_value_p, max_tu_readings=max_value_u, last_updated=last_hour_datetime)


    
    



        for index in range(len(purchase_data)):
                logger.debug(f'Purchase trace_id: {purchase_data[index]["trace_id"]}')
        for index in range(len(upload_data)):
                logger.debug(f'Upload trace_id: {upload_data[index]["trace_id"]}')
            
        logger.debug(f'Updated Statistics Values - num_tp_readings: {stats.num_tp_readings}, num_tu_readings: {stats.num_tu_readings}, max_tp_readings: {stats.max_tp_readings}, max_tu_readings: {stats.max_tu_readings}, last_updated: {stats.last_updated}')

        

   

    # Handle the case where there are no statistics in the table
    # print("5")
       
    #the format of the datetime might be wrong here?
    # print("6")
    

    #consistent with processing and storage
    #storage wlil convert datetime
    #make sure to convert datetime from db to str

    # print('7')
    # print(purchase_data.status_code)

    logger.info("yes")
    # logger.info(f"{purchase_data.status_code}")
    

    logger.info(f"Number of purchase events received: {len(purchase_data)}. Number of upload events received: {len(upload_data)}")
    stats = Stats(num_tp_readings=most_recent_statistic.num_tp_readings + len(purchase_data), num_tu_readings=most_recent_statistic.num_tu_readings + len(upload_data), max_tp_readings=max_value_p, max_tu_readings=max_value_u, last_updated=end_timestamp)
    
    
    



    
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
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
    'interval',
    seconds=app_config['scheduler']['period_sec'])
    sched.start()

def get_stats():
    logger.info("Request has started")
    session = DB_SESSION()
    
    most_recent_statistic = session.query(Stats).order_by(Stats.id.desc()).first()
    
    if most_recent_statistic is None:
         logger.error("ERROR, NOTHING IN DATA IN TABLES")
         return "Statistics do not exist", 404
    # stats_dict = most_recent_statistic.json()
    pydict = {"num_tp_readings": most_recent_statistic.num_tp_readings,
              "num_tu_readings":most_recent_statistic.num_tu_readings,
              "max_tp_readings": most_recent_statistic.max_tp_readings,
              "max_tu_readings": most_recent_statistic.max_tu_readings,}
    session.close()
    logger.info("Request has completed")
    return pydict, 200
    

    


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)
     

if __name__ == "__main__":  
# run our standalone gevent server
    init_scheduler()
    app.run(port=8100)


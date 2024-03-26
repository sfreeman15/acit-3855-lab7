from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime

class EventLogs(Base):
    """ Processing Event Log Messages """
    __tablename__ = "event_log"

    event_id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    message_code = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False)

    def __init__(self, message, message_code,
                 date_time):
        """ Initializes a processing statistics object """
        self.message = message
        self.message_code = message_code
        if date_time is None:
            self.date_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        else:
            self.date_time = date_time
    def to_dict(self):
        """ Dictionary Representation of statistics """
        dict = {}

        dict["message"] = self.message
        dict["message_code"] = self.message_code
        dict["date_time"] = self.date_time
        return dict

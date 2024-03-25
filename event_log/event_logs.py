from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base

class EventLogs(Base):
    """ Processing Event Log Messages """
    __tablename__ = "event_log"

    event_id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    message_code = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False)

    def __init__(self, event_id, message, message_code,
                 date_time):
        """ Initializes a processing statistics object """
        self.event_id = event_id
        self.message = message
        self.message_code = message_code
        self.date_time = date_time

    def to_dict(self):
        """ Dictionary Representation of statistics """
        stats_dict = {
            'event_id': self.event_id,
            'message': self.message,
            'message_code': self.message_code,
            'date_time': self.date_time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        return stats_dict

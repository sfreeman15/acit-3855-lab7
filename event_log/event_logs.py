from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base

class EventLogs(Base):
    """ Processing Event Log Messages """
    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    message_code = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False)

    def __init__(self, id, message, message_code,
                 date_time):
        """ Initializes a processing statistics object """
        self.id = id
        self.message = message
        self.message_code = message_code
        self.date_time = date_time

    def to_dict(self):
        """ Dictionary Representation of statistics """
        stats_dict = {
            'id': self.id,
            'message': self.message,
            'message_code': self.message_code,
            'date_time': self.date_time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        return stats_dict

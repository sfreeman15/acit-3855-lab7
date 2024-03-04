from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base

class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_tp_readings = Column(Integer, nullable=False)
    num_tu_readings = Column(Integer, nullable=False)
    max_tp_readings = Column(Float, nullable=True)
    max_tu_readings = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_tp_readings, num_tu_readings,
                 max_tp_readings, max_tu_readings, last_updated):
        """ Initializes a processing statistics object """
        self.num_tp_readings = num_tp_readings
        self.num_tu_readings = num_tu_readings
        self.max_tp_readings = max_tp_readings
        self.max_tu_readings = max_tu_readings
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of statistics """
        stats_dict = {}
        stats_dict['num_tp_readings'] = self.num_tp_readings,
        stats_dict['num_tu_readings']= self.num_tu_readings,
        stats_dict['max_tp_readings'] = self.max_tp_readings,
        stats_dict['max_tu_readings'] = self.max_tu_readings,
        stats_dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        return stats_dict

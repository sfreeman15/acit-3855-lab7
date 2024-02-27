from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime
import uuid


class TicketUpload(Base): #extends aSQLAlchemy Base class
    """ Ticket Upload """

    __tablename__ = "ticket_upload"
    __table_args__ = {'extend_existing': True} 

    #determine wheter this table is allowed to 
    #add new columns for its inheriting classes, or to 'extend'


    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(250), nullable=False)
    seller_name = Column(String(250), nullable=False)
    concert_name = Column(String(250), nullable=False)
    seat_number = Column(String(250), nullable=False)
    artist = Column(String(250), nullable=False)
    date = Column(String(100))
    venue = Column(String(250))
    price = Column(Float, nullable = False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable = False)

    def __init__(self, ticket_id, seller_name, seat_number, artist, concert_name, date, venue, price, trace_id): #i removed trace id here
        """ Initializes a blood pressure reading """
        self.ticket_id = ticket_id
        self.seller_name = seller_name
        self.seat_number = seat_number
        self.concert_name = concert_name
        self.date = date
        self.venue = venue
        self.price = price
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id
        self.artist = artist
  

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['ticket_id'] = self.ticket_id
        dict['seller_name'] = self.seller_name
        dict['seat_number'] = self.seat_number
        dict['concert_name'] = self.concert_name
        dict['artist'] = self.artist
        dict['date'] = self.date
        dict["venue"] = self.venue
        dict["price"] = self.price
        dict["trace_id"] = self.trace_id
        dict['date_created'] = self.date_created

        return dict

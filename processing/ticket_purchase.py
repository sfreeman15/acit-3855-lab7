from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime
import uuid


class TicketPurchase(Base): #extends aSQLAlchemy Base class
    """ Ticket Purchase """

    __tablename__ = "ticket_purchase"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(250), nullable=False)
    seat_number = Column(String(250), nullable=False)
    concert_name = Column(String(250), nullable=False)
    date = Column(String(100))
    artist = Column(String(250), nullable=False)
    venue = Column(String(250))
    price = Column(Float, nullable = False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable = False)

    def __init__(self, ticket_id, concert_name,artist, seat_number, date, venue, price, trace_id):
        """ Initializes a blood pressure reading """
        self.ticket_id = ticket_id
        self.concert_name = concert_name
        self.seat_number = seat_number
        self.artist = artist
        self.date = date
        self.venue = venue
        self.price = price
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id


    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['ticket_id'] = self.ticket_id
        dict['concert_name'] = self.concert_name
        dict["seat_number"] = self.seat_number
        dict["artist"] = self.artis
        dict['date'] = self.date
        dict["venue"] = self.venue
        dict["price"] = self.price
        dict["trace_id"] = self.trace_id
        dict['date_created'] = self.date_created

        return dict

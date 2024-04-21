from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey


class Gyma(Base):
    """ Activity of going to the gym. """
    __tablename__ = 'gyma'

    gyma_id = Column("gyma_id", Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    time_of_arrival = Column("time_of_arrival", DateTime, nullable=False)
    time_of_leaving = Column("time_of_leaving", DateTime, nullable=True)
    # location_id = Column(Integer, ForeignKey("location.location_id"), nullable=True)

    def set_time_of_leaving(self, time_of_leaving):
        """ Set time of leaving. """
        if self.time_of_leaving is not None:
            raise ValueError("Time of leaving is already set")
        if time_of_leaving <= self.time_of_arrival:
            raise ValueError("Time of leaving must be after time of arrival.")

        self.time_of_leaving = time_of_leaving

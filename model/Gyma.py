from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey


class Gyma(Base):
    """ Activity of going to the gym. """
    __tablename__ = 'gyma'

    gyma_id = Column("gyma_id", Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    time_of_arrival = Column("time_of_arrival", DateTime, nullable=False)
    time_of_leaving = Column("time_of_leaving", DateTime, nullable=True)
    location_id = Column(Integer, ForeignKey("location.location_id"), nullable=True)

    location = relationship("Location", backref="gyma")
    gyma_exercises = relationship("GymaExercise", back_populates="gyma")
    exercises = relationship("Exercise", secondary="gyma_exercise")

    def set_time_of_leaving(self, time_of_leaving):
        """ Set time of leaving. """
        if self.time_of_leaving is not None:
            raise ValueError("Time of leaving is already set")
        if time_of_leaving <= self.time_of_arrival:
            raise ValueError("Time of leaving must be after time of arrival.")

        self.time_of_leaving = time_of_leaving

    def get_exercises(self):
        """
        Returns a list of all Exercise objects associated with this Gyma instance
        through the gyma_exercise relationship.
        """
        if self.exercises:
            return self.exercises.all()
        else:
            raise ValueError("No exercises found for this gyma")

    def get_gyma_city(self):
        """ Returns the city name of gyma, if it exists."""
        if self.location:
            return self.location.city
        else:
            raise ValueError("No city found for this gyma")

    def get_gyma_country(self):
        """ Returns the country of gyma, if it exists."""
        if self.location:
            return self.location.country
        else:
            raise ValueError("No country found for this gyma")

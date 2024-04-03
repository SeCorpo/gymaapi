from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey


class GymaExercise(Base):
    """ Connection between Gyma and Exercise. """
    __tablename__ = 'gyma_exercise'

    ge_id = Column("ge_id", Integer, primary_key=True, autoincrement=True, nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id"), nullable=False)
    gyma_id = Column(Integer, ForeignKey("gyma.gyma_id"), nullable=False)

    exercise = relationship("Exercise", backref="gyma_exercises")
    gyma = relationship("Gyma", backref="gyma_exercises")

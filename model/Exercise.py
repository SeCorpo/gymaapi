from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, VARCHAR, Enum, DateTime


class Exercise(Base):
    """ Characteristics of a gym exercise. """
    __tablename__ = 'exercise'

    exercise_id = Column("exercise_id", Integer, primary_key=True, autoincrement=True, nullable=False)
    exercise_name = Column("exercise_name", VARCHAR(64), nullable=False)
    exercise_type = Column("exercise_type", Enum('gains', 'cardio', 'other'), nullable=False)
    count = Column("count", Integer, nullable=True)
    sets = Column("sets", Integer, nullable=True)
    weight = Column("weight", Integer, nullable=True)
    minutes = Column("minutes", Integer, nullable=True)
    km = Column("km", Integer, nullable=True)
    level = Column("level", Integer, nullable=True)
    description = Column("description", VARCHAR(64), nullable=True)
    created_at = Column("created_at", DateTime, nullable=False)

    gyma_exercises = relationship("GymaExercise", backref="exercise")
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, VARCHAR, Enum, Date, ForeignKey, Text


class Person(Base):
    """ Personal information of users, including settings. """
    __tablename__ = 'person'

    person_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True, nullable=False, index=True)
    first_name = Column("first_name", VARCHAR(64), nullable=False)
    last_name = Column("last_name", VARCHAR(64), nullable=False)
    date_of_birth = Column("date_of_birth", Date, nullable=False)
    sex = Column("sex", Enum('m', 'f', 'o'), nullable=False)
    # country = Column(VARCHAR(64), ForeignKey('country.country_name'), nullable=False)
    city = Column("city", VARCHAR(64), nullable=True)
    profile_text = Column("profile_text", Text, nullable=True)
    gyma_share = Column("gyma_share", Enum("solo", "gymbros", "pub"), nullable=False, default="gymbros")

    gyma = relationship("Gyma", backref="person")
    user = relationship("User", backref="person")

    def get_all_gyma(self):
        if self.gyma:
            return self.gyma
        else:
            return None

    def get_last_three_gyma(self):
        """Returns a query object containing the last 3 gyma visits ordered by time_of_leaving."""
        if self.gyma:
            return self.gyma.order_by(self.gyma.time_of_leaving.desc()).limit(3)
        else:
            return None

    def get_last_gyma(self):
        """Returns a query object containing the last gyma ordered by time_of_leaving."""
        if self.gyma:
            return self.gyma.order_by(self.gyma.time_of_leaving.desc()).first()
        else:
            return None


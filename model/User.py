from database import Base
from sqlalchemy import Column, Integer, VARCHAR, Enum, Boolean


class User(Base):
    __tablename__ = 'user'

    user_id = Column("user_id", Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column("email", VARCHAR(length=255), unique=True, nullable=False, index=True)
    password_hash = Column("password_hash", VARCHAR(length=255), nullable=False)
    account_type = Column("account_type", Enum("admin", "user"), nullable=False, default="user")
    account_active = Column("account_active", Boolean, default=True, nullable=False)
    gyma_share = Column("gyma_share", Enum("solo", "gymbros", "pub"), nullable=False, default="gymbros")

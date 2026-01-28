from data.config.base import Base
from sqlalchemy import Column, String, Integer, Boolean


class UserV2(Base):

    __tablename__ = "userV2"

    id = Column(Integer, primary_key=True)

    name = Column(String(30), nullable=False)
    user = Column(String(30), nullable=False, unique=True)
    password = Column(String(30), nullable=False)

    theme_color = Column(String(15), nullable=False)
    theme_light = Column(String(15), nullable=False)

    photo = Column(String, nullable=True)
    photo_skype = Column(String, nullable=True)

    usr_group = Column(String(30), nullable=False)
    usr_active = Column(Boolean, nullable=False)
    usr_connected = Column(Boolean, nullable=False)
    usr_session = Column(String, nullable=True)

    asanaID = Column(String(30), nullable=False)

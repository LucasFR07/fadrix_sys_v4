from data.config.base import Base
from sqlalchemy import Column, String, Integer, Boolean


class User(Base):

    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    user = Column(String(30), nullable=False, unique=True)
    password = Column(String(30), nullable=False)
    icon = Column(String, nullable=False)
    theme = Column(String(3), nullable=False)
    group = Column(String(30), nullable=False)
    asanaID = Column(String(30), nullable=False)
    active = Column(Boolean, nullable=False)
    connected = Column(Boolean, nullable=False)


    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, user={self.user!r}, password={self.password!r}, icon={self.icon!r}, theme={self.theme!r}, group={self.group!r},  asanaID={self.asanaID!r}, active={self.active!r}), connected={self.connected!r})"

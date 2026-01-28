from data.config.base import Base
from sqlalchemy import Column, String, Integer, Boolean


class Integration(Base):

    __tablename__ = "integration"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    group = Column(String(30), nullable=False)
    multiple = Column(Boolean, nullable=False)
    icon = Column(String, nullable=False)


    def __repr__(self):
        return f"Integration(id={self.id!r}, name={self.name!r}, group={self.group!r}, multiple={self.multiple!r}, icon={self.icon!r})"

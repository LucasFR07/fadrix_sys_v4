from data.config.base import Base
from sqlalchemy import Column, String, Integer


class ThemeColor(Base):

    __tablename__ = "theme_color"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    mode = Column(String(30), nullable=False)
    analog = Column(String(7), nullable=True)
    primary = Column(String(7), nullable=True)
    secondary = Column(String(7), nullable=True)
    info = Column(String(7), nullable=True)
    success = Column(String(7), nullable=True)
    warning = Column(String(7), nullable=True)
    danger = Column(String(7), nullable=True)
    bg = Column(String(7), nullable=True)
    light = Column(String(7), nullable=True)
    dark = Column(String(7), nullable=True)
    white = Column(String(7), nullable=True)
    black = Column(String(7), nullable=True)
    gray = Column(String(7), nullable=True)

    
    
    def __repr__(self):
        return f"ThemeColor(id={self.id!r}, name={self.name!r}, mode={self.mode!r}, analog={self.analog!r}, primary={self.primary!r}, secondary={self.secondary!r}, info={self.info!r}, success={self.success!r}, warning={self.warning!r}, danger={self.danger!r}, bg={self.bg!r}, light={self.light!r}, dark={self.dark!r}, white={self.white!r}, black={self.black!r}, gray={self.gray!r}"

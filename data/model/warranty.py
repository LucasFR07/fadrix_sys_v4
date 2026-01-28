from data.config.base import Base
from sqlalchemy import Column, String, Integer, DateTime, JSON


class Warranty(Base):

    __tablename__ = "warranty"

    id = Column(Integer, primary_key=True)
    sign = Column(String, nullable=False, unique=True)
    status = Column(String(30), nullable=False)
    date = Column(DateTime, index=True, nullable=False)
    user = Column(String(30), nullable=False)

    order_ref = Column(String, nullable=False)
    order_channel = Column(String, nullable=False)
    order_buyer = Column(String, nullable=False)

    shipping_address = Column(JSON, nullable=False)
    shipping_method = Column(String(30), nullable=True)
    shipping_date = Column(DateTime, index=True, nullable=False)
    shipping_tracking = Column(String(30), nullable=True)

    reason = Column(Integer, nullable=False)
    liable = Column(String, nullable=True)

    note = Column(String, nullable=True)
    task_id = Column(JSON, nullable=True)
    historic = Column(String, nullable=False)

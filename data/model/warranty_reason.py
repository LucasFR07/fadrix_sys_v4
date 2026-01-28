from data.config.base import Base
from sqlalchemy import Column, String, Integer, Boolean


class WarrantyReason(Base):

    __tablename__ = "warranty_reason"

    id = Column(Integer, primary_key=True)
    reason = Column(String, nullable=False)
    asana_id = Column(String(30), nullable=True)
    active = Column(Boolean, nullable=False)
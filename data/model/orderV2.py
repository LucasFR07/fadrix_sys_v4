from data.config.base import Base
from sqlalchemy import Column, String, Integer, JSON, Date, DateTime


class OrderV2(Base):

    __tablename__ = "orderV2"

    id = Column(Integer, primary_key=True)
    order_status = Column(String(30), nullable=True)
    order_dateImport = Column(DateTime, index=True, nullable=False)
    order_userSystem = Column(String(30), nullable=False)

    order_number = Column(String(30), nullable=False)
    order_reference = Column(String(30), nullable=True)
    order_channel = Column(String(30), nullable=False)
    order_company = Column(String(30), nullable=False)
    order_date = Column(DateTime, index=True, nullable=False)

    order_customer = Column(String, nullable=False)
    order_customerID = Column(String, nullable=True)
    order_customerNickname = Column(String, nullable=True)
    order_customerPhone = Column(String, nullable=True)
    order_customerEmail = Column(String, nullable=True)

    order_shippingAddress = Column(JSON, nullable=False)
    order_shippingMethod = Column(String(30), nullable=False)
    order_shippingDate = Column(DateTime, index=True, nullable=False)
    order_shippingDateMKP = Column(DateTime, index=True, nullable=True)
    order_shippingTracking = Column(String(30), nullable=True)

    order_task = Column(JSON, nullable=False)
    order_historic = Column(String, nullable=True)


    def __repr__(self):
        return f"Order(id={self.id!r}, order_status={self.order_status!r}, order_dateImport={self.order_dateImport!r}, order_userSystem={self.order_userSystem!r}, order_number={self.order_number!r}, order_reference={self.order_reference!r}, order_channel={self.order_channel!r}, order_company={self.order_company!r}, order_date={self.order_date!r}, order_customer={self.order_customer!r}, order_customerID={self.order_customerID!r}, order_customerNickname={self.order_customerNickname!r}, order_customerPhone={self.order_customerPhone!r}, order_customerEmail={self.order_customerEmail!r}, order_shippingAddress={self.order_shippingAddress!r}, order_shippingMethod={self.order_shippingMethod!r}, order_shippingDate={self.order_shippingDate!r}, order_shippingDateMKP={self.order_shippingDateMKP!r}, order_shippingTracking={self.order_shippingTracking!r}, order_task={self.order_task!r}, order_historic={self.order_historic!r}"

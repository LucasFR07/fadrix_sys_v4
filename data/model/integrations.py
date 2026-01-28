from data.config.base import Base
from sqlalchemy import Column, String, Integer, Boolean


class Integrations(Base):

    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    company = Column(String(30), nullable=True)
    user = Column(String, nullable=True)
    password = Column(String, nullable=True)
    code = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    token_expiration = Column(String, nullable=True)
    app_id = Column(String, nullable=True)
    app_key = Column(String, nullable=True)
    shop_id = Column(String, nullable=True)
    description = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)


    def __repr__(self):
        return f"Integrations(id={self.id!r}, name={self.name!r}, company={self.company!r}, user={self.user!r}, password={self.password!r}, code={self.code!r}, access_token={self.access_token!r}, refresh_token={self.refresh_token!r}, token_expiration={self.token_expiration!r}, app_id={self.app_id!r}, app_key={self.app_key!r}, shop_id={self.shop_id!r}, description={self.description!r}, active={self.active!r})"

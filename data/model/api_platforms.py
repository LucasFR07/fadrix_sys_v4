from data.config.base import Base
from sqlalchemy import Column, String, Integer, Boolean


class API_Platforms(Base):

    __tablename__ = "api_platforms"

    id = Column(Integer, primary_key=True)

    api_platform = Column(String(30), nullable=False)
    api_production_environment = Column(String, nullable=False)
    api_test_environment = Column(String, nullable=True)
    api_version = Column(Integer, nullable=False)

    developer_account = Column(String(30), nullable=True)
    user_account = Column(String, nullable=True)

    login_user = Column(String, nullable=True)
    login_passwd = Column(String, nullable=True)

    access_code = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    access_token_refresh = Column(String, nullable=True)
    access_token_expiration = Column(String, nullable=True)

    test_access_code = Column(String, nullable=True)
    test_access_token = Column(String, nullable=True)
    test_access_token_refresh = Column(String, nullable=True)
    test_access_token_expiration = Column(String, nullable=True)

    app_id = Column(String, nullable=True)
    app_key = Column(String, nullable=True)
    app_key_expiration = Column(String, nullable=True)

    test_app_id = Column(String, nullable=True)
    test_app_key = Column(String, nullable=True)
    test_app_key_expiration = Column(String, nullable=True)

    description = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)


    def __repr__(self):
        return f"API_Platforms(id={self.id!r}, api_platform={self.api_platform!r}, api_production_environment={self.api_production_environment!r}, api_test_environment={self.api_test_environment!r}, api_version={self.api_version!r}, developer_account={self.developer_account!r}, user_account={self.user_account!r}, login_user={self.login_user!r}, login_passwd={self.login_passwd!r}, access_code={self.access_code!r}, access_token={self.access_token!r}, access_token_refresh={self.access_token_refresh!r}, access_token_expiration={self.access_token_expiration!r}, test_access_code={self.test_access_code!r}, test_access_token={self.test_access_token!r}, test_access_token_refresh={self.test_access_token_refresh!r}, test_access_token_expiration={self.test_access_token_expiration!r}, app_id={self.app_id!r}, app_key={self.app_key!r}, app_key_expiration={self.app_key_expiration!r}, test_app_id={self.test_app_id!r}, test_app_key={self.test_app_key!r}, test_app_key_expiration={self.test_app_key_expiration!r}, description={self.description!r}, active={self.active!r})"

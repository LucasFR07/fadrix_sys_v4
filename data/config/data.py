from data.config.connection import DBConnectionHandler
from data.config.base import Base

from data.model.carrier import Carrier
from data.model.comments import Comments
from data.model.company import Company
from data.model.integration import Integration
from data.model.integrations import Integrations
from data.model.log import Log
from data.model.order_product import OrderProduct
from data.model.order import Order
from data.model.quotation import Quotation
from data.model.saleschannel import SalesChannel
from data.model.sector_product import SectorProduct
from data.model.sector import Sector
from data.model.status import Status
# from data.model.task import Task
from data.model.theme_color import ThemeColor
from data.model.user import User
# from data.model.warranty import Warranty


def create_all_tables():
    Base.metadata.create_all(DBConnectionHandler().get_engine())

def initial_data():
    from data.repository.theme_color import ThemeColorRepository as COLOR
    from data.repository.user import UserRepository as USER
    try:
        COLOR().insert(
            name="cosmo",
            mode="light", 
            analog="#6112FD", 
            primary="#1D49FA", 
            secondary="#1072E3", 
            info="#12BCFD", 
            success="#3ECC0E", 
            warning="#CCB00E", 
            danger="#CC0E0E", 
            bg="#CEE2FA", 
            light="#F5F5F5", 
            dark="#232323", 
            white="#FFFFFF", 
            black="#000000", 
            gray="#D3D3D3"           
        )
        USER().insert(
            name="Admin System",
            user="admin@fadrixsys",
            password="123456",
            icon="assets/images/system/profile_default.png",
            theme="1",
            group="Administrador",
            asanaID="1202884793734117",
            active=True,
            connected=False
        )
    except:
        return None

def start_data():
    create_all_tables()
    initial_data()
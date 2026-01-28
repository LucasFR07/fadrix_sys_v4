from data.config.connection import DBConnectionHandler
from data.model.theme_color import ThemeColor
from sqlalchemy.orm.exc import NoResultFound

class ThemeColorRepository():

    def filter_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(ThemeColor).filter(ThemeColor.id==id).one()
                return data
            except NoResultFound:
                return None

    def filter_name(self, name):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(ThemeColor).filter(ThemeColor.name==name).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(ThemeColor).all()
                return data
            except NoResultFound:
                return None

    def insert(self, name, mode, analog, primary, secondary, info, success, warning, danger, bg, light, dark, white, black, gray):
        with DBConnectionHandler() as db:
            try:
                data_insert = ThemeColor(
                    name=name,
                    mode=mode, 
                    analog=analog, 
                    primary=primary, 
                    secondary=secondary, 
                    info=info, 
                    success=success, 
                    warning=warning, 
                    danger=danger, 
                    bg=bg, 
                    light=light, 
                    dark=dark, 
                    white=white, 
                    black=black, 
                    gray=gray
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(ThemeColor).filter(ThemeColor.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, value):
        with DBConnectionHandler() as db:
            try:
                db.session.query(ThemeColor).filter(ThemeColor.id==id).update({fild:value})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

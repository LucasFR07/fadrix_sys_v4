from data.config.connection import DBConnectionHandler
from data.model.company import Company
from sqlalchemy.orm.exc import NoResultFound

class CompanyRepository:

    def filter_id(self, id:int):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Company).filter(Company.id==id).one()
                return data
            except NoResultFound:
                return None
            
    def filter_name(self, name:str):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Company).filter(Company.name==name).one()
                return data
            except NoResultFound:
                return None

    def filter_all(self):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Company).all()
                return data
            except NoResultFound:
                return None

    def insert(self, name, razao, cnpj, ie, phone, address, active, icon, asanaID):
        with DBConnectionHandler() as db:
            try:
                data_insert = Company(name=name, razao=razao, cnpj=cnpj, ie=ie, phone=phone, address=address, active=active, icon=icon, asanaID=asanaID)
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception                

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Company).filter(Company.id==id).delete()
                db.session.commit() 
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, value):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Company).filter(Company.id==id).update({fild:value})
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

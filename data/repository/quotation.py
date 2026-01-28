from data.config.connection import DBConnectionHandler
from data.model.quotation import Quotation
from sqlalchemy.orm.exc import NoResultFound
from controllers.date_control import date_create as date

class QuotationRepository:

    def filter_id(self, id):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Quotation).filter(Quotation.id==id).one()
                return data 
            except NoResultFound:
                return None  
            
    def filter_number(self, num):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Quotation).filter(Quotation.quote_number==num).one()
                return data 
            except NoResultFound:
                return None  
            
    def filter_reference(self, ref):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Quotation).filter(Quotation.quote_reference==ref).all()
                return data 
            except NoResultFound:
                return None            

    def filter_receiver(self, receiver):
        with DBConnectionHandler() as db:
            try:
                data = db.session.query(Quotation).filter(Quotation.destination_address["receiver"].like(f'%{receiver}%')).all()
                return data 
            except NoResultFound:
                return None                        
                             
    def filter_all(self):
        with DBConnectionHandler() as db:
            data = db.session.query(Quotation).all()
            return data

    def insert(self, status, user, date, quote_reference, quote_gateway, origin_address, destination_address, packing, carrier):
        with DBConnectionHandler() as db:
            try:
                data_insert = Quotation(
                    status=status,
                    user=user,
                    date=date,                    
                    quote_number=self.__quote_number(quote_gateway),
                    quote_reference=quote_reference,quote_gateway=quote_gateway, origin_address=origin_address, destination_address=destination_address, packing=packing,
                    carrier=carrier
                )
                db.session.add(data_insert)
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception 

    def delete(self, id):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Quotation).filter(Quotation.id==id).delete()
                db.session.commit()
            except Exception as exception:
                db.session.rollback()
                raise exception

    def update(self, id, fild, data):
        with DBConnectionHandler() as db:
            try:
                db.session.query(Quotation).filter(Quotation.id==id).update({fild:data})
                db.session.commit() 
            except Exception as exception:
                db.session.rollback()
                raise exception

    def __quote_number(self, gtw):

        number = None
        search_quote = self.filter_all()

        if len(search_quote) == 0:
            number = 1
        else:
            with DBConnectionHandler() as db:
                try:
                    data = db.session.query(Quotation).order_by(Quotation.id.desc()).first()
                    number = int(data.id) + 1
                except NoResultFound:
                    return None

        match gtw:
            case "1": #Correios
                code = "C"
            case "2": #Frenet
                code = "F"
            case "3": #Kangu
                code = "K"
            case "4": #MelhorEnvio
                code = "M"
            case _:
                code = "Q"

        quote_number = f'{code}{date().strftime("%y")}{date().month:02}{date().day:02}-{id}'
        return quote_number

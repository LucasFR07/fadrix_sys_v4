from source.api.magis5 import Magis5
from datetime import datetime


class Magis5GET():
    """ Classe para obter as informações do pedido no Magis5, e retorná-lo caso encontre."""

    def __init__(self, order_id:str) -> None:
        self.order_id = order_id
        self.magis5_api = Magis5()


    def get_order(self) -> dict:
        """ Busca um pedido no Magis5 e retorna os dados padronizados para o template.
        
        return {
            "order_found":True,
            "error":"",
            "magis5_id": get_order_in_magis5["id"],
            "magis5_status": None,
            "marketplace_id": get_order_in_magis5["externalId"],
            "marketplace_name": get_order_in_magis5["channelName"],
            "buyer_name": get_order_in_magis5["buyer"]["full_name"].title(),
            "invoice_number": get_order_in_magis5["invoices"]["number"],
            "invoice_access_code": get_order_in_magis5["invoices"]["key"],
            "invoice_xml": get_order_in_magis5["invoices"]["urlXml"],
            "tracking_code": get_order_in_magis5["shipping"]["shipping_number"]
        }

        """

        get_order_in_magis5 = self.magis5_api.get_orders(order_number=self.order_id)

        if "Error" in get_order_in_magis5:
            if get_order_in_magis5['Error']['Code'] == "NOT_FOUND":
                return {"order_found":False, "error": f"Pedido #{self.order_id} não encontrado no Magis5 HUB."}

            return {"order_found":False, "error": get_order_in_magis5['Error']["Message"]}

        channelName = get_order_in_magis5["channelName"].strip().split()[0].capitalize() if get_order_in_magis5["channelName"].strip().split()[0] != "Api" else "Prestashop"

        return {
            "order_found":True,
            "error":"",
            "magis5_id": get_order_in_magis5["id"],
            "magis5_status": self.magis5_api.set_orderStatus(status=get_order_in_magis5["status"]),
            "marketplace_id": get_order_in_magis5["externalId"],
            "marketplace_name": channelName,
            "buyer_name": get_order_in_magis5["buyer"]["full_name"].title(),
            "invoice_number": get_order_in_magis5["invoices"][0]["number"] if len(get_order_in_magis5["invoices"]) != 0 else " -- ",
            "invoice_key": get_order_in_magis5["invoices"][0]["key"] if len(get_order_in_magis5["invoices"]) != 0 else " -- ",
            "invoice_xml": get_order_in_magis5["invoices"][0]["urlXml"] if len(get_order_in_magis5["invoices"]) != 0 else " -- ",
            "tracking_code": get_order_in_magis5["shipping"]["shipping_number"] if "shipping_number" in get_order_in_magis5["shipping"] != 0 else " -- "
        }

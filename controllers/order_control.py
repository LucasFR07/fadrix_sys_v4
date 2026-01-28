## Conexão com Dados
from data.repository.carrier import CarrierRepository as CARRIER
from data.repository.saleschannel import SalesChannelRepository as CHANNEL
## Conexão com APIs
from source.api.meliApi import MercadoLivre as MELI
from source.api.shopeeApi import Shopee as SHOPEE
from source.api.amazonApi import Amazon as AMAZON
from source.api.americanasApi import Americanas
from source.api.prestashopApi import Prestashop
from source.api.iderisV3 import IderisV3
from source.api.tinyApi import Tiny
from source.api.sheinApi import Shein
# from source.api.magaluApi import Magalu
from source.api.magaluApiV1 import MagaluV1 as Magalu
from source.api.magis5 import Magis5
from source.api.tiktokshop import TikTokShop as TIKTOK



from controllers.date_control import date_create as DATE
from datetime import datetime
from pytz import timezone
import json


class OrderControl():

    """ Clase de controle de busca e importação de pedidos em todas as integrações. """

    def __init__(self, number:str, hub:str, cart:bool=False, shop:str=None, company:str=None):

        self.order_number = number.strip()
        self.order_hub = hub
        self.order_cart = cart
        self.order_shop = shop
        self.order_company = company
        self.order_response = None


    def verify_order(self):

        """ Função para filtrar o canal de venda para determinal em qual integração buscar o pedido. """

        try:
            ## DEFINE A PLATAFORMA PARA BUSCAR O PEDIDO:
            match self.order_hub:

                case "americanas_api":
                    self.order_response = Americanas(developer_account=self.order_company).order_pattern(ordem_number=self.order_number)
                    if 'Error' in self.order_response:
                        return self.order_response
                    search_channel = CHANNEL().filter_marketplace(self.order_response["orderChannel"])
                    for chn in search_channel:
                        if chn.company["name"] == self.order_company:
                            channel = chn
                    self.order_response["hub"] = "AmericanasAPI"

                case "iderisV3":
                    self.order_response = IderisV3().order_pattern(order_number=self.order_number, pack_order=self.order_cart)
                    if 'Error' in self.order_response:
                        return self.order_response
                    channel = CHANNEL().filter_ideris(self.order_response["orderChannelID"])
                    self.order_response["hub"] = "IderisV3"

                case "magalu_api":
                    self.order_response = Magalu(developer_account=self.order_company).order_pattern(ordem_number=self.order_number)
                    # print(f'\nGET ORDER FROM MAGALU_API ==> {self.order_response}\n') #DEBUG
                    if 'Error' in self.order_response:
                        return self.order_response
                    search_channel = CHANNEL().filter_marketplace(self.order_response["orderChannel"])
                    for chn in search_channel:
                        if chn.company["name"] == self.order_company:
                            channel = chn
                    self.order_response["hub"] = "MagaluAPI"

                case "magis5hub":
                    self.order_response = Magis5().order_pattern(order_number=self.order_number)
                    if 'Error' in self.order_response:
                        return self.order_response

                    list_companys = {"FBF COMUNICACAO":"FBF", "FENIX SUBLIMACAO":"FENIX", "XDRI SUBLIMACAO":"XDRI"}

                    for chn in CHANNEL().filter_all():
                        if chn.name == self.order_response["orderChannel"] and list_companys[chn.company["name"]] == self.order_response["orderCompany"]:
                            channel = chn
                    self.order_response["hub"] = "Magis5HUB"

                case "meli_api":
                    self.order_response = MELI(developer_account=self.order_company).order_pattern(order_number=self.order_number)
                    # print(f'\nGET ORDER FROM MERCADOLIVRE_API ==> {self.order_response}\n') #DEBUG
                    if 'Error' in self.order_response:
                        return self.order_response
                    search_channel = CHANNEL().filter_marketplace(self.order_response["orderChannel"])
                    for chn in search_channel:
                        if chn.company["name"] == self.order_company:
                            channel = chn
                    self.order_response["hub"] = "MercadoLivreAPI"

                case "prestashop":
                    self.order_response = Prestashop().order_pattern(order_number=self.order_number, shop_id=self.order_shop)
                    # print(f'\nGET ORDER FROM PRESTASHOP ==> {self.order_response}\n') #DEBUG
                    if 'Error' in self.order_response:
                        return self.order_response
                    channel = CHANNEL().filter_ideris(self.order_response["orderChannelID"])
                    self.order_response["hub"] = "Prestashop"

                case "shein_api":
                    self.order_response = Shein(developer_account=self.order_company).order_pattern(order_number=self.order_number) ## NEW
                    # print(f'\nGET ORDER FROM SHEIN_API ==> {self.order_response}\n') #DEBUG
                    if 'Error' in self.order_response:
                        return self.order_response
                    search_channel = CHANNEL().filter_marketplace(self.order_response["orderChannel"])
                    for chn in search_channel:
                        if chn.company["name"] == self.order_company:
                            channel = chn
                    self.order_response["hub"] = "SheinAPI"

                case "shopee_api":
                    self.order_response = SHOPEE(developer_account=self.order_company).order_pattern(order_number=self.order_number) #NEW
                    # print(f'\nGET ORDER FROM SHOPEE_API ==> {self.order_response}\n') #DEBUG
                    if 'Error' in self.order_response:
                        return self.order_response
                    search_channel = CHANNEL().filter_marketplace(self.order_response["orderChannel"])
                    for chn in search_channel:
                        if chn.company["name"] == self.order_company:
                            channel = chn
                    self.order_response["hub"] = "ShopeeAPI"

                case "tiktok_api":
                    self.order_response = TIKTOK(developer_account=self.order_company).order_pattern(order_number=self.order_number) #NEW
                    # print(f'\nGET ORDER FROM TIKTOK_API ==> {self.order_response}\n') #DEBUG
                    if 'Error' in self.order_response:
                        return self.order_response
                    search_channel = CHANNEL().filter_marketplace(self.order_response["orderChannel"])
                    for chn in search_channel:
                        if chn.company["name"] == self.order_company:
                            channel = chn
                    self.order_response["hub"] = "TikTokAPI"

                case "tiny":
                    self.order_response = Tiny(self.order_company).obter_pedido(pedido=self.order_number)
                    # print(f'\nGET ORDER FROM TINYERP ==> {self.order_response}\n') #DEBUG
                    if 'Error' in self.order_response:
                        return self.order_response
                    channel = CHANNEL().filter_tiny(self.order_response["orderChannelID"])
                    self.order_response["hub"] = "TinyERP"

            ## DEFINE A EMPRESA (CONTA) DO CANAL DE VENDA
            if channel != None:
                self.order_response["orderCompany"] = {"id": channel.company["id"], "name": channel.company["name"]}
                self.order_response["orderChannel"] = {"id": channel.asanaID, "name": channel.name}
            else:
                self.order_response["orderCompany"] = {"id": "1206496392745624", "name": "NULL"}
                self.order_response["orderChannel"] = {"id": "1206496517531241", "name": "NULL"}

            ## OBTEM DADOS POR CANAL DE VENDA:
            match self.order_response["orderChannel"]["name"]:

                case "Prestashop":
                    try:
                        get_carrier = CARRIER().filter_integration(intrg="Prestashop", cod=self.order_response["shippingMethod"])
                        self.order_response["shippingMethod"]= {"id": get_carrier.asanaID, "name": get_carrier.name} if get_carrier != None or len(get_carrier) != 0 else {"id": "1204067809318932", "name": "NULL"}

                    except Exception as exc:
                        print(f'ORDER_CONTROL() Erro aos buscar dados da Prestashop -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

                case "Amazon":
                    try:
                        carrier = CARRIER().filter_id(1)
                        self.order_response["shippingMethod"]= {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}

                    except Exception as exc:
                        print(f'ORDER_CONTROL() ==> Erro aos buscar dados da Amazon -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

                case "Americanas":

                    try:

                        if self.order_hub == "americanas_api":
                            carrier = CARRIER().filter_id(self.order_response["shippingMethod"])
                            self.order_response["shippingMethod"] = {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}

                        else:
                            carrier = CARRIER().filter_id(2)
                            self.order_response["shippingMethod"]= {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}

                    except Exception as exc:
                        print(f'ORDER_CONTROL() ==> Erro aos buscar dados da Americanas -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

                case "Magazine Luiza":
                    try:
                        get_carrier = CARRIER().filter_id(3)
                        self.order_response["shippingMethod"]= {"id": get_carrier.asanaID, "name": get_carrier.name} if get_carrier != None else {"id": "1204067809318932", "name": "NULL"}

                    except Exception as exc:
                        print(f'ORDER_CONTROL() ==> Erro aos buscar dados da Magalu -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

                case "Mercado Livre":
                    try:

                        if self.order_hub == "meli_api":
                            carrier = CARRIER().filter_id(self.order_response["shippingMethod"])
                            self.order_response["shippingMethod"] = {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}

                        else:
                            carrier = CARRIER().filter_id(4)
                            self.order_response["shippingMethod"]= {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}                            

                    except Exception as exc:
                        print(f'ORDER_CONTROL() ==> Erro aos buscar dados do Mercado Livre -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

                case "Shopee":
                    try:

                        if self.order_hub == "shopee_api":
                            carrier = CARRIER().filter_id(self.order_response["shippingMethod"])
                            self.order_response["shippingMethod"] = {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}

                        else:
                            carrier = CARRIER().filter_id(5)
                            self.order_response["shippingMethod"]= {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}

                    except Exception as exc:
                        print(f'ORDER_CONTROL() ==> Erro aos buscar dados da Shopee -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

                case "Shein":
                    try:
                        # if self.order_hub != "shein_api":
                        #     get_shipment_date = Shein(self.order_response["orderCompany"]["name"]).get_shipments_date(self.order_number)
                        #     self.order_response["shippingDate"] = get_shipment_date
                        #     self.order_response["original_shippingDate"] = get_shipment_date

                        get_carrier = CARRIER().filter_id(24)
                        self.order_response["shippingMethod"] = {"id": get_carrier.asanaID, "name": get_carrier.name} if get_carrier != None else {"id": "1204067809318932", "name": "NULL"}

                    except Exception as exc:
                        print(f'ORDER_CONTROL() ==> Erro aos buscar dados da Shein -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

                case "TikTok":
                    try:
                        carrier = CARRIER().filter_id(25)
                        self.order_response["shippingMethod"]= {"id": carrier.asanaID, "name": carrier.name} if carrier != None else {"id": "1204067809318932", "name": "NULL"}

                    except Exception as exc:
                        print(f'ORDER_CONTROL() ==> Erro aos buscar dados do TikTok -- {exc}')
                        self.order_response["shippingMethod"]= {"id": "1204067809318932", "name": "NULL"}

            return self.order_response

        except Exception as exc:
            import traceback
            print(f'\n[ERRO] ORDER_CONTROL - VERIFY_ORDER() ==> EXCEPTION: {exc}\n')
            traceback.print_exc()
            return { "Error": {"Code": "000", "Message": f"Erro Interno: {str(exc)}"}}

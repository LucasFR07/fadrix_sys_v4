import requests, json
from datetime import datetime, time
from pytz import timezone
from source.api.api import API


class MercadoLivre(API):

    """
    Classe para gerenciamento e controle da integração com a API do Mercado Livre.

    Cada método abaixo representa um recurso da api disponibilizado pela Mercado Livre,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self, developer_account:str) -> None:
        super().__init__(developer_account, api_platform="Mercado Livre")
        self.get_access()

        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }



    def __check_api_call(call): ## DECORADOR DE CHECAGEM
        """ Verifica a chamada da API, padronizando e resolvendo retornos de erro. """

        try:
            def wrapper(self, *args, **kwargs):
                request_attempts = 1
                for _ in range(2):
                    request_call = call(self, *args, **kwargs)

                    if request_call == None:
                        return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno ao solicitar essa chamada, consulte o suporte do sistema."}}

                    print(f'\n🐞 MERCADOLIVRE_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG
                    deserialize_response = json.loads(request_call.text)

                    if 'message' in deserialize_response:
                        match deserialize_response['message']:

                            case 'invalid access token':
                                self.__refresh_code()
                                request_attempts +=1
                                continue

                            case 'Order do not exists':
                                return {"Error": {"Code": "NOT_FOUND", "Message": "Pedido não encontrado."}}

                            case _:
                                return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API Mercado Livre, consulte o suporte do sistema."}}

                    break

                if call.__name__ == "authorization_code" or call.__name__ == "__refresh_code":
                    self.update_access(
                        new_access_token = deserialize_response["access_token"],
                        new_refresh_token = deserialize_response["refresh_token"]
                    )
                    self.headers['Authorization'] = f'Bearer {deserialize_response["access_token"]}'
                    return None

                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## AUTHORIZATION PROCESS ------

    @__check_api_call
    def authorization_code(self) -> requests.Response | None:
        """ Recurso para que o código de autorização seja trocado por um access token. """

        try:
            path = f'{self.api_production_environment}/oauth/token'
            payload = f'grant_type=authorization_code&client_id={self.app_id}&client_secret={self.app_key}&code={self.access_code}&redirect_uri=https%3A%2F%2Ffadrix.com.br%2F'
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            request_resource = requests.post(url=path, headers=headers, data=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > authorization_code() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __refresh_code(self) -> requests.Response | None:
        """ Recurso para renovar access token. """

        try:
            path = f'{self.api_production_environment}/oauth/token'
            payload = f'grant_type=refresh_token&client_id={self.app_id}&client_secret={self.app_key}&refresh_token={self.access_token_refresh}&redirect_uri=https%3A%2F%2Ffadrix.com.br%2F'
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            request_resource = requests.post(url=path, headers=headers, data=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __refresh_code() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def order_id(self, order_number:str) -> requests.Response:
        """ Recurso para consultar detalhes detalhes de um pedido. """

        try:
            path = f'{self.api_production_environment}/orders/{order_number}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __order_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __pack_id(self, pack_id:str) -> requests.Response:
        """ Recurso para buscar pedidos de carrinho. """

        try:
            path = f'{self.api_production_environment}/packs/{pack_id}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __pack_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __item_id(self, item_id:str) -> requests.Response:
        """ Recurso para buscar informações de produtos. """

        try:
            path = f'{self.api_production_environment}/items/{item_id}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __item_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def shipment_id(self, shipment_id:str) -> requests.Response:
        """ Recurso para buscar informações de envio. """

        try:
            path = f'{self.api_production_environment}/shipments/{shipment_id}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __shipments_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def user_id(self) -> requests.Response:
        """ Recurso para buscar informações do vendedor. """

        try:
            path = f'{self.api_production_environment}/users/{self.user_account}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __user_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def user_questions_response_time(self) -> requests.Response:
        """ Recurso para buscar métricas de tempo de respostas do vendedor. """

        try:
            path = f'{self.api_production_environment}/users/{self.user_account}/questions/response_time'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __user_questions_response_time() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def schedule(self, logistic_type:str) -> requests.Response:
        """ Recurso para consultar o horário de despacho dos pedidos. """

        try:
            path = f'{self.api_production_environment}/users/{self.user_account}/shipping/schedule/{logistic_type}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > schedule() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def shipping_preferences(self) -> requests.Response:
        """ Recurso para consultar o horário de despacho dos pedidos. """

        try:
            path = f'{self.api_production_environment}/users/{self.user_account}/shipping_preferences'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > shipping_preferences() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def shipment_tracking(self, shipment_id:str) -> requests.Response:
        """ Recurso para consultar as informações de rastreamento da transportadora. """

        try:
            path = f'{self.api_production_environment}/shipments/{shipment_id}/carrier'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > shipment_tracking() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, order_number:str) -> dict | None:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            set_order = self.order_id(order_number)

            if not "Error" in set_order and set_order["pack_id"] != None and order_number != set_order["pack_id"]:
                return {"Error": {"Code": "PACK_ORDER", "Message": "Pedido de carrinho, buscar pelo número do carrinho."}}

            if "Error" in set_order:
                if set_order["Error"]["Code"] == "NOT_FOUND":

                    check_pakc_order = self.__pack_order_pattern(order_number)
                    if check_pakc_order == None:
                        return set_order

                    else:
                        set_order = check_pakc_order

                else:
                    return set_order

            set_shipping = self.shipment_id(set_order["shipping"]["id"])

            return {
                "orderDate": datetime.fromisoformat(set_order["payments"][len(set_order["payments"])-1]["date_created"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": order_number,
                "orderReference": None,
                "orderChannel": "Mercado Livre",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": f'{set_order["buyer"]["first_name"]} {set_order["buyer"]["last_name"]}'.title(),
                "customerID": set_order["buyer"]["id"],
                "customerNickname": set_order["buyer"]["nickname"],
                "customerPhone": None,
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_shipping["receiver_address"]["street_name"]}, n{set_shipping["receiver_address"]["street_number"]}, {set_shipping["receiver_address"]["comment"]}, {set_shipping["receiver_address"]["neighborhood"]["name"]}, {set_shipping["receiver_address"]["city"]["name"]}, {set_shipping["receiver_address"]["state"]["name"]}, CEP: {set_shipping["receiver_address"]["zip_code"]} - Quem Recebe: {set_shipping["receiver_address"]["receiver_name"]}',

                    "endereco": set_shipping["receiver_address"]["street_name"],

                    "numero": set_shipping["receiver_address"]["street_number"],

                    "complemento": set_shipping["receiver_address"]["comment"],

                    "bairro": set_shipping["receiver_address"]["neighborhood"]["name"],

                    "cidade": set_shipping["receiver_address"]["city"]["name"],

                    "uf": set_shipping["receiver_address"]["state"]["name"],

                    "cep": set_shipping["receiver_address"]["zip_code"],

                    "destinatario": set_shipping["receiver_address"]["receiver_name"],

                },
                "shippingMethod": self.__shipping_method_rule(set_shipping['logistic_type']),
                "shippingDate": datetime.fromisoformat(set_order["manufacturing_ending_date"]).astimezone(tz=timezone('America/Sao_Paulo')) if set_order["manufacturing_ending_date"] != None else datetime.combine(date=datetime.now().date(), time=time(23, 59, 59), tzinfo=timezone('America/Sao_Paulo')),
                "original_shippingDate": datetime.fromisoformat(set_order["manufacturing_ending_date"]).astimezone(tz=timezone('America/Sao_Paulo')) if set_order["manufacturing_ending_date"] != None else datetime.combine(date=datetime.now().date(), time=time(23, 59, 59), tzinfo=timezone('America/Sao_Paulo')),
                "shippingTracking": None,
                "Products": [
                    {
                        "id": item["item"]["id"],
                        "produto": item["item"]["title"],
                        "sku": item["item"]["seller_custom_field"] if item["item"]["seller_custom_field"] != None else item["item"]["seller_sku"],
                        "qtd": item["quantity"],
                        "icon": self.__product_image_pattern(product_id=item["item"]["id"], variation_id=item["item"]["variation_id"]),
                        "personalizacao": ", ".join([f'{va["name"]}: {va["value_name"]}' for va in item["item"]["variation_attributes"]]) if len(item["item"]["variation_attributes"]) != 0 else ""
                    }
                    for item in set_order["order_items"]
                ],
            }

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > order_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def __pack_order_pattern(self, pack_number:str):
        """ Busca o número do pedido original em pedidos de carrinho para importação no sistema. """

        try:
            set_pack_order = self.__pack_id(pack_number)

            if "Error" in set_pack_order:
                return None

            join_orders = list()
            for order in set_pack_order["orders"]:
                get_order = None
                get_order = self.order_id(order["id"])
                join_orders.append(get_order["order_items"][0])

            get_order["order_items"] = join_orders
            return get_order

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __pack_order_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def __product_image_pattern(self, product_id:str, variation_id:str=None) -> str:
        """ Faz a busca de informações de pedidos e retorna a URL da imagem do produto para importação no sistema. """

        try:
            set_product = self.__item_id(product_id)

            if len(set_product["variations"]) != 0:
                for variation in set_product["variations"]:
                    if variation["id"] == variation_id:
                        return f'https://http2.mlstatic.com/D_{variation["picture_ids"][0]}-O.jpg'

            else:
                return f'https://http2.mlstatic.com/D_{set_product["thumbnail_id"]}-O.jpg'

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __product_image_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def __shipping_method_rule(self, logistic_type:str) -> int | None:
        """ Define e retorna o ID da forma de envio (Correios, Agência, Coleta, Flex) de acordo com o retorno da API para importação no sistema. """

        try:

            match logistic_type:
                case 'drop_off':
                    return 17 #Mercado Envios Correios
                case 'xd_drop_off':
                    return 18 #Mercado Envios Agência
                case 'cross_docking':
                    return 19 #Mercado Envios Coleta
                case 'self_service':
                    return 23 #Mercado Envios Flex
                case _:
                    return 4 #Mercado Envios

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > __shipping_method_rule() ==> EXCEPTION {exc}\n') ##DEBUG
            return 4 #Mercado Envios


    def dispatch_schedule(self):
        """ Retorna o horário de despacho do dia de acordo com o tipo de logística da loja. """

        try:
            get_logistic_type = self.shipping_preferences()
            set_logistic_type = None

            for log in get_logistic_type["logistics"]:
                if log["mode"] == "me2":
                    for type_log in log["types"]:
                        if type_log["type"] not in ["self_service", "fulfillment"]:
                            set_logistic_type = type_log["type"]

            match set_logistic_type:
                case 'drop_off':
                    set_logistic_name = "Mercado Envios Correios"
                case 'xd_drop_off':
                    set_logistic_name = "Mercado Envios Agência"
                case 'cross_docking':
                    set_logistic_name = "Mercado Envios Coleta"
                case 'self_service':
                    set_logistic_name = "Mercado Envios Flex"
                case _:
                    set_logistic_name = "Mercado Envios"

            get_dispatch_schedule = self.schedule(logistic_type=set_logistic_type)

            weekday_list = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
            weekday_name = weekday_list[datetime.now().weekday()]
            set_weekday = get_dispatch_schedule["schedule"][weekday_name]

            return {
                "schedule_start": set_weekday["detail"][0]["from"],
                "schedule_end": set_weekday["detail"][0]["to"],
                "cutting_time": set_weekday["detail"][0]["cutoff"],
                "logistic_type": set_logistic_name,
                "carrier": set_weekday["detail"][0]["carrier"]["name"],
                "driver": set_weekday["detail"][0]["driver"]["name"],
                "vehicle_plate": set_weekday["detail"][0]["vehicle"]["license_plate"]
            }

        except Exception as exc:
            print(f'\n❌ MERCADOLIVRE_API > dispatch_schedule() ==> EXCEPTION {exc}\n') ##DEBUG
            return None

    ## ------

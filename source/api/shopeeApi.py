import time
import requests, hmac, json, time, hashlib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from source.api.api import API


class Shopee(API):

    """
    Classe para gerenciamento e controle da integração com a API da Shopee.

    Cada método abaixo representa um recurso da api disponibilizado pela Shopee,
    com excessão dos métodos terminados em "pattern", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self, developer_account:str) -> None:
        super().__init__(developer_account, api_platform="Shopee")
        self.get_access()



    def __check_api_call(call): ## DECORADOR DE CHECAGEM
        """ Verifica a chamada da API, padronizando e resolvendo retornos de erro. """

        try:
            def wrapper(self, *args, **kwargs):
                request_attempts = 1
                for _ in range(2):
                    request_call = call(self, *args, **kwargs)

                    if request_call == None:
                        return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno ao solicitar essa chamada, consulte o suporte do sistema."}}

                    print(f'\n🐞 SHOPEE_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG
                    deserialize_response = json.loads(request_call.text)

                    match deserialize_response["message"]:

                        case "Invalid access_token." | "Invalid access_token, please have a check.":
                            self.__get_access_token_shop_level()

                        case "Wrong parameters, detail: the order is not found.":
                            return {"Error": {"Code": {request_call.status_code}, "Message": f"Pedido não encontrado na conta Shopee selecionada:{self.developer_account}."}}

                        case "User is forbidden for this action.":
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API Shopee, verifique a conta Shopee selecionada, ou consulte o suporte do sistema."}}

                        case "":
                            if call.__name__ == "__get_access_token_shop_level" or call.__name__ == "get_token_shop_level":

                                self.update_access(
                                    new_access_token=deserialize_response["access_token"],
                                    new_refresh_token=deserialize_response["refresh_token"]
                                )

                            return deserialize_response

                        case _:
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API Shopee, consulte o suporte do sistema."}}

                    request_attempts +=1

            return wrapper

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## AUTHORIZATION PROCESS ------

    def __sign(self, path:str, timestamp:int) -> str:
        """ Cria e retorna uma string padrão com carimbo para realizar as chamadas da API. """

        try:
            tmp_base_string = "%s%s%s%s%s" % (int(self.app_id), path, timestamp, self.access_token, int(self.user_account))
            base_string = tmp_base_string.encode()
            sign = hmac.new(self.app_key.encode(), base_string, hashlib.sha256).hexdigest()
            return sign

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __sign() ==> EXCEPTION IN SING: {exc}\n')
            return None


    def __required_parameters(self, path:str) -> str:
        """ Cria e retorna uma string padrão com todos os parâmetros obrigatórios incluidos para realizar as chamadas da API. """

        try:
            timestamp = int(time.time())
            return f'{path}?partner_id={int(self.app_id)}&timestamp={timestamp}&access_token={self.access_token}&shop_id={int(self.user_account)}&sign={self.__sign(path=path, timestamp=timestamp)}'

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __required_parameters() ==> EXCEPTION: {exc}\n')
            return None


    @__check_api_call
    def get_token_shop_level(self, code:str) -> requests.Response | None:
        """ Obtem o token de acesso para chamadas da API. """

        try:
            timest = int(time.time())
            path = "/api/v2/auth/token/get"
            tmp_base_string = "%s%s%s" % (int(self.app_id), path, timest)
            sign = hmac.new(self.app_key.encode(), tmp_base_string.encode(), hashlib.sha256).hexdigest()

            url = "https://partner.shopeemobile.com" + path + "?partner_id=%s&timestamp=%s&sign=%s" % (int(self.app_id), timest, sign)
            headers = {"Content-Type": "application/json"}
            body = {"code":code, "shop_id":int(self.user_account), "partner_id":int(self.app_id)}

            request_resource = requests.post(url, json=body, headers=headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __get_token_shop_level() ==> EXCEPTION: {exc}\n')
            return None


    @__check_api_call
    def __get_access_token_shop_level(self) -> requests.Response | None:
        """ Renova o token de acesso para chamadas da API. """

        try:
            timest = int(time.time())
            path = "/api/v2/auth/access_token/get"
            tmp_base_string = "%s%s%s" % (int(self.app_id), path, timest)
            sign = hmac.new(self.app_key.encode(), tmp_base_string.encode(), hashlib.sha256).hexdigest()

            url = "https://openplatform.shopee.com.br" + path + "?partner_id=%s&timestamp=%s&sign=%s" % (int(self.app_id), timest, sign)
            headers = {"Content-Type": "application/json"}
            body = {"shop_id": int(self.user_account), "refresh_token": self.access_token_refresh, "partner_id": int(self.app_id)}

            request_resource = requests.post(url, json=body, headers=headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __get_access_token_shop_level() ==> EXCEPTION: {exc}\n')
            return None

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def get_order_detail(self, order_number:str) -> requests.Response | None:
        """ Use esta API para obter detalhes do pedido. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/order/get_order_detail")}&order_sn_list={order_number}&response_optional_fields=buyer_user_id,buyer_username,recipient_address,note,item_list,package_list,shipping_carrier,total_amount,checkout_shipping_carrier,edt,prescription_images,prescription_check_status'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __get_order_detail() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_order_list(self, filter_time_range_field:str="create_time", filter_time_from:str=None, filter_time_to:str=None, filter_order_status:str="READY_TO_SHIP", next_cursor:str='', logistics_channel_id:str='') -> requests.Response | None:
        """ Use esta api para pesquisar pedidos. Você também pode filtrá-los por status, se necessário. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/order/get_order_list")}&time_range_field={filter_time_range_field}&time_from={filter_time_from}&time_to={filter_time_to}&order_status={filter_order_status}&page_size=100&cursor={next_cursor}{logistics_channel_id}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_order_list() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_item_base_info(self, item_id=int) -> requests.Response | None:
        """ Use esta API para obter informações básicas do item pela lista item_id. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/product/get_item_base_info")}&item_id_list={item_id}&need_tax_info=true'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __get_item_base_info() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def __get_shipment_list(self, cursor:str="") -> requests.Response | None:
        """ Use esta API para obter a lista de pedidos cujo status é READY_TO_SHIP para iniciar o processamento de todo o andamento do envio. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/order/get_shipment_list")}&page_size=100&cursor={cursor}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_shipment_list() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_shipping_parameter(self, order_number:str) -> requests.Response | None:
        """ Use esta api para obter o parâmetro "info_needed" da resposta para verificar se o pedido tem retirada ou entrega ou nenhuma opção de integração. Esta api também retornará os endereços e as opções de id de horário de retirada para o método de retirada. Para entrega, ela pode retornar id da agência, nome real do remetente etc., dependendo dos requisitos do 3PL. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters(path="/api/v2/logistics/get_shipping_parameter")}&order_sn={order_number}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_shipping_parameter() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_tracking_number(self, order_number:str) -> requests.Response | None:
        """ Após organizar o envio (v2.logistics.ship_order) para o canal integrado, use esta api para obter o tracking_number, que é um parâmetro necessário para criar etiquetas de envio. A resposta da api pode retornar tracking_number vazio, já que esta informação depende do 3PL, devido a isso é permitido continuar chamando a api dentro de um intervalo de 5 minutos, até que o tracking_number seja retornado. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters(path="/api/v2/logistics/get_tracking_number")}&order_sn={order_number}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_tracking_number() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_tracking_info(self, order_number:str) -> requests.Response | None:
        """ Use esta API para obter informações de rastreamento logístico de um pedido. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters(path="/api/v2/logistics/get_tracking_info")}&order_sn={order_number}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_tracking_info() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_conversation_list(self, cursor="") -> requests.Response | None:
        """ - """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/sellerchat/get_conversation_list")}&direction=older&type=all&next_timestamp_nano={cursor}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_conversation_list() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_message(self, conversation_id:str) -> requests.Response | None:
        """ - """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/sellerchat/get_message")}&conversation_id={conversation_id}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_message() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def send_message(self, user_id:int, msg:str) -> requests.Response | None:
        """ - """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/sellerchat/send_message")}'
            payload=json.dumps({"content": {"text": msg}, "message_type": "text", "to_id": user_id})
            headers = {'Content-Type': 'application/json'}
            request_resource = requests.request("POST", path, headers=headers, data=payload, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > send_message() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def shop_performance(self) -> requests.Response | None: #deprecated
        """ As métricas de dados do desempenho da loja. Esta API será descontinuada em 2024.09.30, mude para usar v2.account_health.get_shop_performance. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/account_health/shop_performance")}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > shop_performance() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def shop_penalty(self) -> requests.Response | None:
        """" Para obter informações sobre a penalidade da loja. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/account_health/shop_penalty")}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > shop_penalty() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None


    @__check_api_call
    def get_shop_performance(self) -> requests.Response | None:
        """" As métricas de dados do desempenho da loja. """

        try:
            path = f'{self.api_production_environment}{self.__required_parameters("/api/v2/account_health/get_shop_performance")}'
            request_resource = requests.request("GET", path, headers={}, data={}, allow_redirects=False)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_shop_performance() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n') ##DEBUG
            return None

    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, order_number:str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            get_order_detail = self.get_order_detail(order_number)

            if "Error" in get_order_detail:
                return get_order_detail

            set_order = get_order_detail['response']['order_list'][0]

            if set_order['order_status'] == 'CANCELLED':
                return {"Error": {"Code": 'CANCELLED', "Message": f"Pedido Shopee #{set_order['order_sn']}, está CANCELADO!"}}

            return {
                "orderDate": datetime.fromtimestamp(set_order['create_time']),
                "orderNumber": set_order['order_sn'],
                "orderReference": None,
                "orderChannel": "Shopee",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": f'{set_order['recipient_address']['name']}'.title(),
                "customerID": set_order['buyer_user_id'],
                "customerNickname": set_order['buyer_username'],
                "customerPhone": set_order['recipient_address']['phone'],
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_order['recipient_address']['full_address'].split(",")[0]}, n{set_order['recipient_address']['full_address'].split(",")[1].strip()}, {set_order['recipient_address']['full_address'].split(",")[2].strip()}, {set_order['recipient_address']['district']}, {set_order['recipient_address']['city']}, {set_order['recipient_address']['state']}, CEP: {set_order['recipient_address']['zipcode']} - Quem Recebe: {set_order['recipient_address']['name']}',
                    "endereco": set_order['recipient_address']['full_address'].split(",")[0],
                    "numero": set_order['recipient_address']['full_address'].split(",")[1].strip(),
                    "complemento": set_order['recipient_address']['full_address'].split(",")[2].strip(),
                    "bairro": set_order['recipient_address']['district'],
                    "cidade": set_order['recipient_address']['city'],
                    "uf": set_order['recipient_address']['state'],
                    "cep": set_order['recipient_address']['zipcode'],
                    "destinatario": set_order['recipient_address']['name']

                },
                "shippingMethod": self.__shipping_method_rule2(order_number=set_order['order_sn'], shipping_carrier=set_order['shipping_carrier']),
                "shippingDate": self.__shipping_date_rule(set_order['ship_by_date']),
                "original_shippingDate": datetime.fromtimestamp(set_order['ship_by_date']),
                "shippingTracking": None,
                "Products": [
                    {
                        "id": item['item_id'],
                        "produto": item['item_name'],
                        "sku": item['model_sku'] if item['model_sku'] != '' else item['item_sku'],
                        "qtd": item['model_quantity_purchased'],
                        "icon": item['image_info']['image_url'],
                        "personalizacao": item['model_name'],
                    }
                    for item in set_order['item_list']
                ],
                "extra_comment_buyer": set_order["message_to_seller"]
            }

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_order_pattern() ==> EXCEPTION IN ORDER PATTERN: {exc}\n') ##DEBUG
            return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno com a padronização do pedido, consulte o suporte do sistema."}}


    def bulk_orders_pattern(self, order_numbers:str) -> list:
        """ Padroniza as informações do pedido para importação em massa no sistema. """

        try:
            get_orders_detail = self.get_order_detail(order_numbers)

            if "Error" in get_orders_detail:
                return get_orders_detail

            set_orders = get_orders_detail['response']['order_list']
            list_orders = list()

            for order in set_orders:

                if order['order_status'] == 'CANCELLED':
                    continue
                    # return {"Error": {"Code": 'CANCELLED', "Message": f"Pedido Shopee #{self.return_order['order_sn']}, está CANCELADO!"}}

                list_orders.append(
                    {
                        "orderDate": datetime.fromtimestamp(order['create_time']),
                        "orderNumber": order['order_sn'],
                        "orderReference": None,
                        "orderChannel": "Shopee",
                        "orderChannelID": None,
                        "orderCompany": self.developer_account,
                        "customer": f'{order['recipient_address']['name']}'.title(),
                        "customerID": order['buyer_user_id'],
                        "customerNickname": order['buyer_username'],
                        "customerPhone": order['recipient_address']['phone'],
                        "order_customerEmail": None,
                        "shippingAddress": {

                            "enderecoCompleto": f'{order['recipient_address']['full_address'].split(",")[0]}, n{order['recipient_address']['full_address'].split(",")[1].strip()}, {order['recipient_address']['full_address'].split(",")[2].strip()}, {order['recipient_address']['district']}, {order['recipient_address']['city']}, {order['recipient_address']['state']}, CEP: {order['recipient_address']['zipcode']} - Quem Recebe: {order['recipient_address']['name']}',
                            "endereco": order['recipient_address']['full_address'].split(",")[0],
                            "numero": order['recipient_address']['full_address'].split(",")[1].strip(),
                            "complemento": order['recipient_address']['full_address'].split(",")[2].strip(),
                            "bairro": order['recipient_address']['district'],
                            "cidade": order['recipient_address']['city'],
                            "uf": order['recipient_address']['state'],
                            "cep": order['recipient_address']['zipcode'],
                            "destinatario": order['recipient_address']['name']

                        },
                        "shippingMethod": self.__shipping_method_rule2(order_number=order['order_sn'], shipping_carrier=order['shipping_carrier']),
                        "shippingDate": self.__shipping_date_rule(order['ship_by_date']),
                        "original_shippingDate": datetime.fromtimestamp(order['ship_by_date']),
                        "shippingTracking": None,
                        "Products": [
                            {
                                "id": item['item_id'],
                                "produto": item['item_name'],
                                "sku": item['model_sku'] if item['model_sku'] != '' else item['item_sku'],
                                "qtd": item['model_quantity_purchased'],
                                "icon": item['image_info']['image_url'],
                                "personalizacao": item['model_name']
                            }
                            for item in order['item_list']
                        ],
                        # "extra_carrier": self.get_shipping_parameter(order['order_sn']),
                        "extra_comment_buyer": order["message_to_seller"]
                    }
                )

            return list_orders

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > bulk_orders_pattern() ==> EXCEPTION: {exc}\n') ##DEBUG
            return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno com a padronização do pedido, consulte o suporte do sistema."}}


    def ready_to_ship_list(self) -> list:
        """ Retorna uma lista com todos os pedidos pendentes para serem emitidos nota fiscal e etiqueta de envio. """

        try:
            list_ship = list()
            next_cursor = ""

            while True:
                get_list_ship = self.__get_shipment_list(cursor=next_cursor)
                if "Error" in get_list_ship:
                    return None

                for order in get_list_ship["response"]["order_list"]:
                    list_ship.append(order)

                if get_list_ship["response"]["more"] == False or get_list_ship["response"]["next_cursor"] == "400":
                    break

                else:
                    next_cursor = get_list_ship["response"]["next_cursor"]
                    continue                    

                # if get_list_ship["response"]["more"] == True:
                #     next_cursor = get_list_ship["response"]["next_cursor"]
                #     continue

                # else:
                #     break

            return list_ship

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > shipment_list_pattern() ==> EXCEPTION IN SHIPMENT PATTERN: {exc}\n') ##DEBUG
            return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno com a padronização do pedido, consulte o suporte do sistema."}}


    def __shipping_date_rule(self, shipping_date:datetime) -> datetime:
        """ Define a data de envio ADT de acordo com a regra interna da empresa. """

        try:
            get_shipping_date = datetime.fromtimestamp(shipping_date)
            get_today = datetime.now()

            if get_shipping_date.day == get_today.day:
                return get_shipping_date

            set_shipping_date_week_day = get_shipping_date.weekday()

            match set_shipping_date_week_day:

                case 0: #SEGUNDA
                    if get_shipping_date.hour < 18:
                        set_shipping_date = get_shipping_date - relativedelta(days=3)
                        return set_shipping_date
                    else:
                        return get_shipping_date

                case 1 | 2 | 3 | 4: #TERÇA, #QUARTA, #QUINTA, #SEXTA
                    if get_shipping_date.hour < 18:
                        set_shipping_date = get_shipping_date - relativedelta(days=1)
                        return set_shipping_date
                    else:
                        return get_shipping_date

                case 5 | 6: #SÁBADO #DOMINGO
                    set_shipping_date = get_shipping_date - relativedelta(days=set_shipping_date_week_day-4)
                    return set_shipping_date


        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __shipping_date_rule() ==> EXCEPTION RULE: {exc}\n') ##DEBUG
            return datetime.fromtimestamp(shipping_date)


    def __shipping_method_rule_DEPRECATED(self, order_number:str) -> int | None:
        """ Define e retorno o ID da forma de envio (Correios, Agência, Coleta) de acordo com o retorno da API para importação no sistema. """

        ## NUM. 20 -> ENVIOS POR CORREIOS
        ## NUM. 21 -> ENVIOS EM AGÊNCIA SHOPEE
        ## NUM. 22 -> ENVIOS COM COLETA SHOPEE
        ## NUM. 5 -> SHOPEE ENVIOS (DEFAUT)

        try:
            get_shipiing_info = self.get_shipping_parameter(order_number)

            if 'dropoff' in get_shipiing_info['response']['info_needed'] and not 'pickup' in get_shipiing_info['response']['info_needed']:
                return 20

            elif 'pickup' in get_shipiing_info['response']['info_needed']:
                return 21 if get_shipiing_info['response']['pickup']['address_list'] == None else 22

            else:
                return 5

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __shipping_method_rule() ==> EXCEPTION {exc}\n') ##DEBUG
            return 5


    def __shipping_method_rule2(self, order_number:str=None, shipping_carrier:str=None) -> int | None:
        """ Define e retorno o ID da forma de envio (Correios, Agência, Coleta) de acordo com o retorno da API para importação no sistema.

        id_shopee_carrir_in_system = {
            "Shopee Envios": 5, #Default
            "Shopee Envios Correios": 20,
            "Shopee Express Agência": 21,
            "Shopee Express Coleta": 22,
            "Shopee Entrega Direta": 26
        }
        """

        try:
            set_shipping_carrier = shipping_carrier
            match set_shipping_carrier:

                case "Correios":
                    return 20

                case "Shopee Xpress" | "Retirar na Agência Shopee":
                    get_shipiing_info = self.get_shipping_parameter(order_number)
                    if not 'Error' in get_shipiing_info:

                        if "dropoff" in get_shipiing_info['response'] and not "pickup" in get_shipiing_info['response']:
                            return 21
                        elif "pickup" in get_shipiing_info['response'] and not "dropoff" in get_shipiing_info['response']:
                            return 22
                        else:
                            return 22

                    return 5

                case "Shopee Entrega Direta":
                    return 26

                case _:
                    return 5


        except Exception as exc:
            print(f'\n❌ SHOPEE_API > __shipping_rule2() ==> EXCEPTION {exc}\n') ##DEBUG
            return 5

    ## ------


    def get_all_orders(self, flex:bool=False) -> list:
        """ Obtem todas os pedidos dentro de 31 dias no painel da Shopee. """

        try:
            flex_logistic = '' if flex == False else '&logistics_channel_id=90022'
            list_all_orders = list()
            set_next_cursor = ''

            for status in ['READY_TO_SHIP', 'PROCESSED']:
                for ranges_timestamps in self.gerar_ranges_timestamps():

                    while True:
                        get_orders_shopee = self.get_order_list(filter_time_from=ranges_timestamps[1], filter_time_to=ranges_timestamps[0], filter_order_status=status, next_cursor=set_next_cursor, logistics_channel_id=flex_logistic)

                        for order in get_orders_shopee['response']['order_list']:
                            list_all_orders.append([order['order_sn'], status])

                        if get_orders_shopee['response']['more'] == False:
                            break

                        else:
                            set_next_cursor = get_orders_shopee['response']['next_cursor']

            print(f'\n🐞 SHOPEE_API ==> TOTAL PEDIDOS ENCONTRADOS: {len(list_all_orders)}\n') ##DEBUG
            return list_all_orders

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > get_all_orders() ==> EXCEPTION: {exc}\n') ##DEBUG
            return []


    def gerar_ranges_timestamps(self, intervalo_dias:int=15):
        """ Gera range de datas para períodos de 31 dias com intervalos de 15 dias. """

        try:
            range_count = 1
            range_times_number = intervalo_dias
            range_times_list =list()
            from_timestamp = datetime.now()

            for _ in range(4):
                to_timestamp = from_timestamp - relativedelta(days=range_times_number)
                print(f'\n🐞 RANGE {range_count} ==> from: {from_timestamp} | to: {to_timestamp}\n')
                range_times_list.append((int(time.mktime(from_timestamp.timetuple())), int(time.mktime(to_timestamp.timetuple()))))
                from_timestamp = to_timestamp + relativedelta(days=1)
                range_count+=1

            print(f'\n🐞 RANGE LIST ==> from: {range_times_list}\n')
            return range_times_list

        except Exception as exc:
            print(f'\n❌ SHOPEE_API > gerar_ranges_timestamps() ==> EXCEPTION: {exc}\n') ##DEBUG
            return []

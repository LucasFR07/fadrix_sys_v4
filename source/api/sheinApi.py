import requests, hmac, json, time, hashlib, base64, random
from datetime import datetime
from pytz import timezone
from dateutil.relativedelta import relativedelta
from controllers.aes_tools import AESTools as AES
from source.api.api import API


class Shein(API):

    """
    Classe para gerenciamento e controle da integração com a API da Shein.

    Cada método abaixo representa um recurso da api disponibilizado pela Shein,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self, developer_account: str) -> None:
        super().__init__(developer_account, api_platform="Shein")
        self.get_access()



    def __check_api_call(call): ## DECORADOR DE CHECAGEM
        """ Verifica a chamada da API, padronizando e resolvendo retornos de erro. """

        try:
            def wrapper(self, *args, **kwargs):
                request_call = call(self, *args, **kwargs)

                if request_call == None:
                    return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno ao solicitar essa chamada, consulte o suporte do sistema."}}

                print(f'\n🐞 SHEIN_API > CHECK_CALL > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG
                deserialize_response = json.loads(request_call.text)

                if deserialize_response["msg"] != "OK":
                    print(f'\n🐞 SHEIN_API > {call.__name__}() ==> ERROR: {deserialize_response["msg"]}\n') ##DEBUG
                    return {"Error": {"Code": "REQUEST_ERROR", "Message": "A chamada retornou um erro, consulte o suporte do sistema."}}

                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ SHEIN_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## AUTHORIZATION PROCESS ------

    def __sign(self, path:str, timestamp:str) -> str:
        """ Cria e retorna uma string padrão com carimbo para realizar as chamadas da API. """

        try:
            openKeyId = self.login_user if self.login_user != None else self.app_id
            secretKey = AES.decrypt(self.login_passwd, self.app_key) if self.login_passwd != None else self.app_key

            # print(f'\n openKeyId ==> {openKeyId}\n')
            # print(f'\n secretKey ==> {secretKey}\n')

            merge_signature_factors = "{}&{}&{}".format(openKeyId, timestamp, path)
            random_key = f'FSY{random.randint(10, 99)}'
            merge_keys = "{}{}".format(secretKey, random_key)
            hash_value = hmac.new(
                key=merge_keys.encode(),
                msg=merge_signature_factors.encode(),
                digestmod= hashlib.sha256
            ).hexdigest()
            sign = f'{random_key}{base64.b64encode(hash_value.encode()).decode()}'
            return sign

        except Exception as exc:
            print(f'\n❌ SHEIN_API > __sign() ==> EXCEPTION IN SING: {exc}\n')
            return None


    def __get_by_token(self) -> None:
        """ Autorização do usuário - obtenha a chave da API e a chave secreta com base no token temporário. """

        try:
            timestamp = str(int(time.time())*1000)
            path = '/open-api/auth/get-by-token'
            headers = {
                "x-lt-appid": self.app_id,
                "x-lt-timestamp": timestamp,
                "x-lt-signature": self.__sign(path, timestamp),
                "Content-Type": "application/json;charset=UTF-8"
            }
            payload = {"tempToken": self.access_code}

            request_resource = requests.post(url=f'{self.api_production_environment}{path}', headers=headers, json=payload)
            print(f'\n🐞 SHEIN_API > __get_by_token() ==> RESPONSE: {request_resource.status_code} | {request_resource.text}\n') ##DEBUG            
            deserialize_response = json.loads(request_resource.text)

            self.update_login(
                new_login_user=deserialize_response["info"]["openKeyId"],
                new_login_passwd=deserialize_response["info"]["secretKey"]
            )

        except Exception as exc:
            print(f'\n❌ SHEIN_API > __get_by_token() ==> EXCEPTION: {exc}\n')
            return None

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def order_list(self, query_type:int=1, order_status:int=1, time_now:datetime=None, time_diff:datetime=None) -> requests.Response | None:
        """ API Para Consultar lista de pedidos. """

        try:
            timenow = datetime.now().astimezone(tz=timezone('America/Sao_Paulo')) if time_now == None else time_now
            timediff = timenow - relativedelta(hours=48) if time_diff == None else time_diff
            timestamp = str(int(time.time())*1000)

            path = '/open-api/order/order-list'
            headers = {
                "x-lt-openKeyId": self.login_user,
                "x-lt-timestamp": timestamp,
                "x-lt-signature": self.__sign(path, timestamp),
                "Content-Type": "application/json;charset=UTF-8"
            }
            payload ={
                "queryType": query_type,
                "startTime": timediff.strftime('%Y-%m-%d %H:%M:%S'),
                "endTime": timenow.strftime('%Y-%m-%d %H:%M:%S'),
                "page": 1,
                "pageSize": 30,
                "orderStatus": order_status
            }

            request_resource = requests.post(url=f'{self.api_production_environment}{path}', headers=headers, json=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHEIN_API > order_list() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def order_detail(self, order_number:list) -> requests.Response | None:
        """ API Para Consultar detalhes do pedido. """

        try:
            timestamp = str(int(time.time())*1000)

            path = '/open-api/order/order-detail'
            headers = {
                "x-lt-openKeyId": self.login_user,
                "x-lt-timestamp": timestamp,
                "x-lt-signature": self.__sign(path, timestamp),
                "Content-Type": "application/json;charset=UTF-8"
            }
            payload = {"orderNoList": order_number}

            request_resource = requests.post(url=f'{self.api_production_environment}{path}', headers=headers, json=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHEIN_API > order_detail() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def export_address(self, order_number:str) -> requests.Response | None:
        """ Exportar (obter) informações de endereço do destinatário. """

        try:
            timestamp = str(int(time.time())*1000)

            path = '/open-api/order/export-address'
            headers = {
                "x-lt-openKeyId": self.login_user,
                "x-lt-timestamp": timestamp,
                "x-lt-signature": self.__sign(path, timestamp),
                "Content-Type": "application/json;charset=UTF-8"
            }
            payload = {"orderNo": order_number, "handleType": 1}

            request_resource = requests.post(url=f'{self.api_production_environment}{path}', headers=headers, json=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHEIN_API > export_address() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def print_express_info(self, order_number:str, package_number) -> requests.Response | None:
        """ API Para a etiqueta de Envio. """

        try:
            timestamp = str(int(time.time())*1000)

            path = '/open-api/order/print-express-info'
            headers = {
                "x-lt-openKeyId": self.login_user,
                "x-lt-timestamp": timestamp,
                "x-lt-signature": self.__sign(path, timestamp),
                "Content-Type": "application/json;charset=UTF-8"
            }
            payload = {"orderNo":order_number, "packageNo":package_number}

            request_resource = requests.post(url=f'{self.api_production_environment}{path}', headers=headers, json=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ SHEIN_API > print_express_info() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, order_number: str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            get_order_detail = self.order_detail([order_number])

            if "Error" in get_order_detail:
                return get_order_detail

            get_shipping = self.export_address(order_number)

            info = get_order_detail["info"][0]
            receive = get_shipping["info"]["receiveMsgList"][0]

            def safe_dt(field_name: str):
                value = info.get(field_name)

                if not isinstance(value, str) or not value.strip():
                    print(f"[WARN] Campo {field_name} veio inválido da SHEIN: {value!r}")
                    return None

                try:
                    dt = datetime.fromisoformat(value)
                    tz = timezone('America/Sao_Paulo')
                    if dt.tzinfo is None:
                        dt = tz.localize(dt)
                    else:
                        dt = dt.astimezone(tz)
                    return dt
                except Exception as exc:
                    print(f"[WARN] Erro ao converter {field_name}={value!r}: {exc}")
                    return None

            order_date = safe_dt("orderAllocateTime")
            shipping_date = safe_dt("requestHandoverTime")
            request_print_time = safe_dt("requestPrintTime")

            return {
                "orderDate": order_date,
                "orderNumber": info["orderNo"],
                "orderReference": None,
                "orderChannel": "Shein",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": f'{receive["firstName"]} {receive["lastName"]}'.title(),
                "customerID": None,
                "customerNickname": None,
                "customerPhone": receive["phone"],
                "order_customerEmail": None,
                "shippingAddress": {
                    "enderecoCompleto": (
                        f'{receive["address"]}, n{receive["addressExt"]}, '
                        f'{receive["district"]}, {receive["city"]}, '
                        f'{receive["province"]}, CEP: {receive["postCode"]} - '
                        f'Quem Recebe: {receive["firstName"]} {receive["lastName"]}'
                    ),
                    "endereco": receive["address"],
                    "numero": receive["addressExt"],
                    "complemento": None,
                    "bairro": receive["district"],
                    "cidade": receive["city"],
                    "uf": receive["province"],
                    "cep": receive["postCode"],
                    "destinatario": f'{receive["firstName"]} {receive["lastName"]}',
                },
                "shippingMethod": None,
                "shippingDate": shipping_date,
                "original_shippingDate": shipping_date,
                "shippingTracking": None,
                "Products": [
                    {
                        "id": item["goodsId"],
                        "produto": item["goodsTitle"],
                        "sku": item["sellerSku"] if item["sellerSku"] != "" else item["skc"],
                        "qtd": 1,
                        "icon": item["spuPicURL"],
                        "personalizacao": (
                            item["skuAttribute"][2]["attrName"]
                            if item.get("skuAttribute")
                            and len(item["skuAttribute"]) > 2
                            and isinstance(item["skuAttribute"][2], dict)
                            else None
                        ),
                    }
                    for item in info["orderGoodsInfoList"]
                    if item["newGoodsStatus"] != 6
                ],
                "requestPrintTime": request_print_time,
            }

        except Exception as exc:
            print(f'\n❌ SHEIN_API > order_pattern() ==> EXCEPTION: {exc}\n')
            return {
                "Error": True,
                "Message": str(exc),
                "OrderNumber": order_number,
            }

    def bulk_orders_pattern(self, order_numbers: list) -> list:
        """ Padroniza as informações do pedido para importação em massa no sistema. """

        try:
            get_order_detail = self.order_detail(order_numbers)

            if "Error" in get_order_detail:
                return get_order_detail

            list_orders = list()

            def safe_dt(order: dict, field_name: str):
                value = order.get(field_name)

                if not isinstance(value, str) or not value.strip():
                    print(f"[WARN] Campo {field_name} veio inválido da SHEIN (bulk): {value!r}")
                    return None

                try:
                    dt = datetime.fromisoformat(value)
                    tz = timezone('America/Sao_Paulo')
                    if dt.tzinfo is None:
                        dt = tz.localize(dt)
                    else:
                        dt = dt.astimezone(tz)
                    return dt
                except Exception as exc:
                    print(f"[WARN] Erro ao converter {field_name}={value!r} em bulk: {exc}")
                    return None

            for order in get_order_detail["info"]:

                get_shipping = self.export_address(order["orderNo"])

                list_orders.append(
                    {
                        "orderDate": safe_dt(order, "orderAllocateTime"),
                        "orderNumber": order["orderNo"],
                        "orderReference": None,
                        "orderChannel": "Shein",
                        "orderChannelID": None,
                        "orderCompany": self.developer_account,
                        "customer": f'{get_shipping["info"]["receiveMsgList"][0]["firstName"]} {get_shipping["info"]["receiveMsgList"][0]["lastName"]}'.title(),
                        "customerID": None,
                        "customerNickname": None,
                        "customerPhone": get_shipping["info"]["receiveMsgList"][0]["phone"],
                        "order_customerEmail": None,
                        "shippingAddress": {
                            "enderecoCompleto": f'{get_shipping["info"]["receiveMsgList"][0]["address"]}, n{get_shipping["info"]["receiveMsgList"][0]["addressExt"]}, {get_shipping["info"]["receiveMsgList"][0]["district"]}, {get_shipping["info"]["receiveMsgList"][0]["city"]}, {get_shipping["info"]["receiveMsgList"][0]["province"]}, CEP: {get_shipping["info"]["receiveMsgList"][0]["postCode"]} - Quem Recebe: {get_shipping["info"]["receiveMsgList"][0]["firstName"]} {get_shipping["info"]["receiveMsgList"][0]["lastName"]}',
                            "endereco": get_shipping["info"]["receiveMsgList"][0]["address"],
                            "numero": get_shipping["info"]["receiveMsgList"][0]["addressExt"],
                            "complemento": None,
                            "bairro": get_shipping["info"]["receiveMsgList"][0]["district"],
                            "cidade": get_shipping["info"]["receiveMsgList"][0]["city"],
                            "uf": get_shipping["info"]["receiveMsgList"][0]["province"],
                            "cep": get_shipping["info"]["receiveMsgList"][0]["postCode"],
                            "destinatario": f'{get_shipping["info"]["receiveMsgList"][0]["firstName"]} {get_shipping["info"]["receiveMsgList"][0]["lastName"]}',
                        },
                        "shippingMethod": 24,
                        "shippingDate": safe_dt(order, "requestHandoverTime"),
                        "original_shippingDate": safe_dt(order, "requestHandoverTime"),
                        "shippingTracking": None,
                        "Products": [
                            {
                                "id": item["goodsId"],
                                "produto": item["goodsTitle"],
                                "sku": item["sellerSku"] if item["sellerSku"] != "" else item["skc"],
                                "qtd": 1,
                                "icon": item["spuPicURL"],
                                "personalizacao": (
                                    item["skuAttribute"][2]["attrName"]
                                    if item.get("skuAttribute")
                                    and len(item["skuAttribute"]) > 2
                                    and isinstance(item["skuAttribute"][2], dict)
                                    else None
                                ),
                            }
                            for item in order["orderGoodsInfoList"]
                            if item["newGoodsStatus"] != 6
                        ],
                        "requestPrintTime": safe_dt(order, "requestPrintTime"),
                    }
                )

            return list_orders

        except Exception as exc:
            print(f'\n❌ SHEIN_API > bulk_orders_pattern() ==> EXCEPTION: {exc}\n')
            return []


    def order_status_pattern(self, order_number:str) -> dict:
        """ Obtem os status do pedido para relatórios do sistema. """

        try:
            get_order_detail = self.order_detail(order_number)

            if "Error" in get_order_detail:
                return get_order_detail

            order_status = {
                1: "Pendente",
                2: "Para Enviar",
                3: "Para ser enviado por SHEIN",
                4: "Enviado",
                5: "Entregue",
                6: "Reembolsado",
                7: "Para ser coletado pela SHEIN",
                8: "Perda Registrada",
                9: "Rejeitado",
            }

            invoice_status = get_order_detail["info"][0]["invoiceStatus"]

            return {
                "status": order_status[get_order_detail["info"][0]["orderStatus"]],
                "nota_fiscal": "Não emitida" if invoice_status == 2 else "Emitida"
            }

        except Exception as exc:
            print(f'\n❌ SHEIN_API > order_status_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def shippingdate_rule(self, orderAllocateTime:str, requestDeliveryTime:str) -> datetime:
        """ Define e retorna a data de envio de acordo com a regra da SHEIN para importação no sistema. """

        try:
            set_orderDate = datetime.fromisoformat(orderAllocateTime).astimezone(tz=timezone('America/Sao_Paulo'))

            match set_orderDate.weekday(): #VERIFICA O DIA DA SEMANA

                case 0 | 1 | 2 | 3:
                    if set_orderDate.hour >=20 and set_orderDate.hour <=23:
                        return set_orderDate + relativedelta(days=1, hour=19, minute=59, second=00)
                    else:
                        return datetime.fromisoformat(requestDeliveryTime).astimezone(tz=timezone('America/Sao_Paulo'))

                case 4:
                    if set_orderDate.hour >=20 and set_orderDate.hour <=23:
                        return set_orderDate + relativedelta(days=3, hour=19, minute=59, second=00)
                    else:
                        return datetime.fromisoformat(requestDeliveryTime).astimezone(tz=timezone('America/Sao_Paulo'))

                case 5:
                    return set_orderDate + relativedelta(days=2, hour=19, minute=59, second=00)

                case 6:
                    return set_orderDate + relativedelta(days=1, hour=19, minute=59, second=00)

        except Exception as exc:
            print(f'\n❌ SHEIN_API > shippingdate_rule() ==> EXCEPTION: {exc}\n')
            return None


    def print_shipping_label(self):
        """ Padroniza o processo de impressão de etiqueta. """

    ## ------

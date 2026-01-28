import time
import requests, hmac, json, time, hashlib
from datetime import datetime, timedelta
from pytz import timezone
from urllib.parse import urlparse  
from dateutil.relativedelta import relativedelta
from source.api.api import API


class TikTokShop(API):

    """
    Classe para gerenciamento e controle da integração com a API do TikTok Shop.

    Cada método abaixo representa um recurso da api disponibilizado pelo TikTok Shop,
    com excessão dos métodos terminados em "pattern", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2025 Douglas Leal
    @license: ****
    """

    def __init__(self, developer_account:str) -> None:
        super().__init__(developer_account, api_platform='TikTok')
        self.get_access()

        self.header = {
            "content-type": "application/json",
            "x-tts-access-token": self.access_token
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

                    print(f'\n🐞 TIKTOK_SHOP_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG
                    deserialize_response = json.loads(request_call.text)

                    match request_call.status_code:

                        case 200:
                            if "access_token" in deserialize_response["data"]:
                                self.update_access(
                                    new_access_token=deserialize_response["data"]["access_token"],
                                    new_refresh_token=deserialize_response["data"]["refresh_token"]
                                )

                            else:
                                return deserialize_response

                        case 401:
                            if deserialize_response["code"] == 105002: ## Refrash Token
                                print(f'\n🐞 TIKTOK_SHOP_API > EXPIRED CREDENTIALS\n')
                                self.generate_refresh_token()

                        case _:
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API TikTok Shop, consulte o suporte do sistema."}}

                    request_attempts +=1

            return wrapper

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None





    ## AUTHORIZATION PROCESS ------

    @__check_api_call
    def generate_access_token(self) -> requests.Response | None:
        """ Obtem o token de acesso para chamadas da API. """

        try:
            path = f"https://auth.tiktok-shops.com/api/v2/token/get?app_key={self.app_id}&app_secret={self.app_key}&auth_code={self.access_code}&grant_type=authorized_code"
            headers = {"Content-Type": "application/json"}
            request_resource = requests.get(url=path, headers=headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > generate_access_token() ==> EXCEPTION: {exc}\n')
            return None

    @__check_api_call
    def generate_refresh_token(self) -> requests.Response | None:
        """ Obtem um novo token de acesso para chamadas da API. """

        try:
            path = f"https://auth.tiktok-shops.com/api/v2/token/refresh?app_key={self.app_id}&app_secret={self.app_key}&refresh_token={self.access_token_refresh}&grant_type=refresh_token"
            headers = {"Content-Type": "application/json"}
            request_resource = requests.get(url=path, headers=headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > generate_refresh_token() ==> EXCEPTION: {exc}\n')
            return None


    def __generate_signature(self, query_parameter:dict, api_path:str, app_secret:str, headers:dict=None, body:dict=None):
        """ Gera a assinatura padrão para requisições da API. """

        try:
            # 1. Ordenar alfabeticamente os parâmetros por chave
            sorted_params = sorted(query_parameter.keys())

            # 2. Concatenar chave=valor
            params_string = ''.join(f"{key}{query_parameter[key]}" for key in sorted_params)

            # 3. Adicionar o caminho da solicitação da API à sequência de assinatura
            signature_string = f"{api_path}{params_string}"

            # 4. Se não houver multipart/form-data e o corpo da solicitação existir, anexe o corpo serializado em JSON
            if body:
                body_string = json.dumps(body)
                signature_string += body_string

            # 5. Envolver string de assinatura com app_secret
            wrapped_string = f"{app_secret}{signature_string}{app_secret}"

            # 4. Gerar HMAC-SHA256
            signature = hmac.new(
                app_secret.encode('utf-8'),
                wrapped_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            return signature



            # print(f'\n🐞 DEBUUG ==> REQUEST_OPTION: {request_option}\n')
            # # Step 1: Extract and filter query parameters, exclude "access_token" and "sign", sort alphabetically
            # # params = request_option.get('qs', {})
            # # print(f'\n🐞 DEBUUG ==> PARAMS: {params}\n')
            # sorted_params = [{"key":key, "value":request_option[key]} for key in sorted(request_option.keys()) if key not in ["access_token", "sign"]]
            # print(f'\n🐞 DEBUUG ==> SORTED_PARAMS: {sorted_params}\n')

            # # Step 2: Concatenate parameters in {key}{value} format
            # param_string = ''.join([f"{item['key']}{item['value']}" for item in sorted_params])
            # sign_string = param_string
            # print(f'\n🐞 DEBUUG ==> PARAM_STRING: {param_string}\n')

            # # Step 3: Append API request path to the signature string
            # uri = request_option.get('uri', '')
            # pathname = urlparse(uri).path if uri else ''
            # sign_string = f"{pathname}{param_string}"
            # print(f'\n🐞 DEBUUG ==> SIGN_STRING: {sign_string}\n')

            # Step 4: If not multipart/form-data and request body exists, append JSON-serialized body
            # content_type = request_option.get('headers', {}).get('content-type', '')
            # body = request_option.get('body', {})
            # if content_type != 'multipart/form-data' and body:
            #     body_str = json.dumps(body)  # JSON serialization ensures consistency
            #     sign_string += body_str

            # # Step 5: Wrap signature string with app_secret
            # wrapped_string = f"{app_secret}{sign_string}{app_secret}"
            # print(f'\n🐞 DEBUUG ==> WRAPPED_STRING: {wrapped_string}\n')

            # # Step 6: Encode using HMAC-SHA256 and generate hexadecimal signature
            # hmac_obj = hmac.new(
            #     app_secret.encode('utf-8'),
            #     wrapped_string.encode('utf-8'),
            #     hashlib.sha256
            # )
            # sign = hmac_obj.hexdigest()
            # return sign

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > __generate_signature() ==> EXCEPTION: {exc}\n')
            return None


    def __common_parameters(self):
        """ When calling any TikTok Shop API, these are the required common parameters. """

        try:
            ...

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > __common_parameters() ==> EXCEPTION: {exc}\n')
            return None

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def get_authorized_shops(self) -> requests.Response | None:
        """ Seller authorization is required before an app can access the data of a shop. Use this API to check which shops are currently authorized for an app and obtain the corresponding shop cipher for use as an input parameter in shop related APIs. """

        __version = 202309

        try:
            path = "/authorization/202309/shops"
            params = {"app_key":self.app_id, "timestamp":int(time.time())}
            signature = self.__generate_signature(query_parameter=params, api_path=path, app_secret=self.app_key)

            request_resource = requests.get(url=f'{self.api_production_environment}{path}?sign={signature}', params=params, headers=self.header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > get_authorized_shops() ==> EXCEPTION: {exc}\n')
            return None


    @__check_api_call
    def get_order_detail(self, order_number:str) -> requests.Response | None:
        """ Get the detailed order information of an order, including important attributes such as order status, shipping addresses, payment details, price and tax info, and package information. """

        __version = 202507

        try:
            path = "/order/202507/orders"
            params = {"app_key":self.app_id, "timestamp":int(time.time()), "shop_cipher":self.user_account, "ids":order_number}
            signature = self.__generate_signature(query_parameter=params, api_path=path, app_secret=self.app_key)

            request_resource = requests.get(url=f'{self.api_production_environment}{path}?sign={signature}', params=params, headers=self.header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > get_order_detail() ==> EXCEPTION: {exc}\n')
            return None

    ## ------



    ## MÉTODOS DO SISTEMA ------
    
    def order_pattern(self, order_number:str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            get_order_detail = self.get_order_detail(order_number)

            if "Error" in get_order_detail:
                return get_order_detail

            set_order = get_order_detail["data"]["orders"][0]

            if set_order["status"] == 'CANCELLED':
                return {"Error": {"Code": 'CANCELLED', "Message": f"Pedido TikTok Shop #{set_order["id"]}, está CANCELADO!"}}

            return {
                "orderDate": datetime.fromtimestamp(set_order["create_time"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": set_order["id"],
                "orderReference": None,
                "orderChannel": "TikTok",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": set_order["cpf_name"].title(),
                "customerID": set_order["user_id"],
                "customerNickname": None,
                "customerPhone": None,
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_order['recipient_address']["address_line2"].title()}, n{set_order['recipient_address']["address_line3"].title()}, {set_order['recipient_address']["address_line4"].title()}, {set_order['recipient_address']["address_line1"].title()}, {set_order['recipient_address']["district_info"][2]["address_name"]}, {set_order['recipient_address']["district_info"][1]["address_name"]}, CEP: {set_order['recipient_address']["postal_code"]} - Quem Recebe: {set_order['recipient_address']["first_name"].title()}',

                    "endereco": set_order['recipient_address']["address_line2"].title(),

                    "numero": set_order['recipient_address']["address_line3"].title(),

                    "complemento": set_order['recipient_address']["address_line4"].title(),

                    "bairro": set_order['recipient_address']["address_line1"].title(),

                    "cidade": set_order['recipient_address']["district_info"][2]["address_name"],

                    "uf": set_order['recipient_address']["district_info"][1]["address_name"],

                    "cep": set_order['recipient_address']["postal_code"],

                    "destinatario": set_order['recipient_address']["first_name"].title()

                },
                "shippingMethod": None,
                "shippingDate": datetime.fromtimestamp(set_order["tts_sla_time"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "original_shippingDate": datetime.fromtimestamp(set_order["tts_sla_time"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "shippingTracking": set_order["packages"][0]["id"],
                "Products": [
                    {
                        "id": item["sku_id"],
                        "produto": item["product_name"],
                        "sku": item["seller_sku"],
                        "qtd": 1,
                        "icon": item["sku_image"],
                        "personalizacao": item["sku_name"],
                    }
                    for item in set_order["line_items"]
                ],
                "extra_comment_buyer": set_order["buyer_message"]
            }

        except Exception as exc:
            print(f'\n❌ TIKTOK_SHOP_API > get_order_pattern() ==> EXCEPTION IN ORDER PATTERN: {exc}\n') ##DEBUG
            return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno com a padronização do pedido, consulte o suporte do sistema."}}


    ## ------    
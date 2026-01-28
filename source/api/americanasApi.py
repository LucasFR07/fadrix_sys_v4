import requests, json
from pathlib import Path
from datetime import datetime
from pytz import timezone
from source.api.api import API



class Americanas(API):

    """
    Classe para gerenciamento e controle da integração com a API da Americanas (B2W).

    Cada método abaixo representa um recurso da api disponibilizado pelo Americanas (B2W),
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self, developer_account:str) -> None:
        super().__init__(developer_account, api_platform="SkyHUB")
        self.get_access()

        self.call_header = {
            'X-User-Email': self.login_user,
            'X-Api-Key': self.access_token,
            'X-Accountmanager-Key': self.login_passwd,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }



    def __check_api_call(call): ## DECORADOR DE CHECAGEM
        """ Verifica a chamada da API, padronizando e resolvendo retornos de erro. """

        try:
            def wrapper(self, *args, **kwargs):
                request_attempts = 1
                for _ in range(2):
                    request_call = call(self, *args, **kwargs)

                    if request_call == None:
                        return {"Error": {"Code": "INTERNAL", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

                    print(f'\n🐞 AMERICANAS_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG

                    match request_call.status_code:

                        case 200: #Successfully
                            break

                        case 404:
                            return {"Error": {"Code": "NOT_FOUND", "Message": "Pedido não encontrado, verifique o número informado e tente novamente."}}

                        case 500:
                            return {"Error": {"Code": "SERVER_FALL", "Message": "Falha no servidor (API) da Americanas, não está respondendo no momento. Aguarde alguns instantes e tente novamente."}}

                        case _:
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API Americanas, consulte o suporte do sistema."}}

                deserialize_response = json.loads(request_call.text)
                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ AMERICANAS_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## RECURSOS DA API ------

    @__check_api_call
    def __orders(self, order_number:str) -> requests.Response | None:
        """ Recurso para consulta de pedidos existentes na conta. """

        try:
            path = f'{self.api_production_environment}/orders/Lojas Americanas-{order_number}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMERICANAS_API > __orders() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __products(self, product_id:str) -> requests.Response | None:
        """ Recurso para consulta de produtos cadastrados na conta. """

        try:
            path = f'{self.api_production_environment}/products/{product_id}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMERICANAS_API > __products() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, ordem_number:str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            set_order = self.__orders(ordem_number)

            if "Error" in set_order:
                return set_order

            return {
                "orderDate": datetime.fromisoformat(set_order["payments"][0]["transaction_date"] if set_order["payments"][0]["transaction_date"] != None else set_order["approved_date"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": set_order["code"],
                "orderReference": None,
                "orderChannel": "Americanas",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": set_order["customer"]["name"].title(),
                "customerID": set_order["customer"]["id_customer"],
                "customerNickname": set_order["customer"]["id_customer"],
                "customerPhone": set_order["customer"]["phones"][0],
                "order_customerEmail": set_order["customer"]["email"],
                "shippingAddress": {

                    "enderecoCompleto": f'{set_order["shipping_address"]["street"]}, n{set_order["shipping_address"]["number"].strip()}, {set_order["shipping_address"]["detail"]}, {set_order["shipping_address"]["neighborhood"]}, {set_order["shipping_address"]["city"]}, {set_order["shipping_address"]["region"]}, CEP: {set_order["shipping_address"]["postcode"]} - Quem Recebe: {set_order["shipping_address"]["full_name"].title()}',

                    "endereco": set_order["shipping_address"]["street"],
                    "numero": set_order["shipping_address"]["number"].strip(),
                    "complemento": set_order["shipping_address"]["detail"],
                    "bairro": set_order["shipping_address"]["neighborhood"],
                    "cidade": set_order["shipping_address"]["city"],
                    "uf": set_order["shipping_address"]["region"],
                    "cep": set_order["shipping_address"]["postcode"],
                    "destinatario": set_order["shipping_address"]["full_name"].title()

                },
                "shippingMethod": 2,
                "shippingDate": datetime.fromisoformat(set_order["expedition_limit_date"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "original_shippingDate": datetime.fromisoformat(set_order["expedition_limit_date"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "shippingTracking": None,
                "Products": self.__product_pattern(products_list=set_order["items"])
            }

        except Exception as exc:
            print(f'\n❌ AMERICANAS_API > order_pattern() ==> EXCEPTION: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}


    def __product_pattern(self, products_list:list) -> list:
        """ Padroniza as informações do produto para importação no sistema. """

        try:
            set_products_list = products_list
            set_products_list_patterned = list()

            for item in set_products_list:
                get_product_info = self.__products(product_id=item["product_id"])

                if "Error" in get_product_info:
                    product_image = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/images/system/nopreview.png"
                    product_customization = ""

                else:
                    if "variations" in get_product_info:
                        for variation in get_product_info["variations"]:
                            if variation["sku"] == item["id"]:
                                product_image = variation['images'][0]
                                product_customization = f'{variation["specifications"][0]["key"]} {variation["specifications"][0]["value"]}'

                    product_image = get_product_info["images"][0]
                    product_customization = ""

                set_products_list_patterned.append(
                    {
                        "id": item["product_id"],
                        "produto": item["name"],
                        "sku": item["id"],
                        "qtd": item["qty"],
                        "icon": product_image,
                        "personalizacao": product_customization
                    }
                )

            return set_products_list_patterned

        except Exception as exc:
            print(f'\n❌ AMERICANAS_API > __product_pattern() ==> EXCEPTION: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------

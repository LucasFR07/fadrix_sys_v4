import requests, json
from datetime import datetime
from pytz import timezone
from source.api.api import API


class Magalu(API):

    """
    Classe para gerenciamento e controle da integração com a API da MAGALU.

    Cada método abaixo representa um recurso da api disponibilizado pela MAGALU,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self, developer_account:str) -> None:
        super().__init__(developer_account, api_platform="Magazine Luiza")
        self.get_access()

        self.call_header = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        self.__auth_url = "https://id.magalu.com/login?client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>&scope=<SCOPES>&response_type=code&choose_tenants=true"



    def __check_api_call(call): ## DECORADOR DE CHECAGEM
        """ Verifica a chamada da API, padronizando e resolvendo retornos de erro. """

        try:
            def wrapper(self, *args, **kwargs):
                request_attempts = 1
                for _ in range(2):
                    request_call = call(self, *args, **kwargs)

                    if request_call == None:
                        return {"Error": {"Code": "INTERNAL", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

                    print(f'\n🐞 MAGALU_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG
                    deserialize_response = json.loads(request_call.text)

                    if 'message' in deserialize_response:
                        match deserialize_response['message']:

                            case 'Unauthorized':
                                self.__refresh_token()
                                request_attempts +=1
                                continue

                            case _:
                                return {"Error": {"Code": "CALL_ERROR", "Message": "Houve um erro na resposta da API, tente novamente ou consulte o suporte do sistema."}}

                    break

                if call.__name__ == "__authorization_code" or call.__name__ == "__refresh_token":
                    self.update_access(
                        new_access_token = deserialize_response["access_token"],
                        new_refresh_token = deserialize_response["refresh_token"]
                    )
                    self.call_header['Authorization'] = f'Bearer {deserialize_response["access_token"]}'
                    return None

                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ MAGALU_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## AUTHORIZATION PROCESS ------

    @__check_api_call
    def __authorization_code(self) -> requests.Response | dict:
        """ A partir do código de autorização concedido pelo usuário, cria um token de acesso às APIs da plataforma. """

        try:
            path = "https://id.magalu.com/oauth/token"
            payload = json.dumps({
                "client_id": self.app_id,
                "client_secret": self.app_key,
                "redirect_uri": "https://fadrix.com.br",
                "code": self.access_code,
                "grant_type": "authorization_code"
            })
            headers = {'Content-Type': 'application/json'}

            request_resource = requests.post(url=path, headers=headers, data=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGALU_API > authorization_code() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}


    @__check_api_call
    def __refresh_token(self) -> requests.Response | dict:
        """ A partir do "refresh_token" atualiza o token de acesso às APIs da plataforma. """

        try:
            path = "https://id.magalu.com/oauth/token"
            payload = f'grant_type=refresh_token&client_id={self.app_id}&client_secret={self.app_key}&refresh_token={self.access_token_refresh}'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            request_resource = requests.post(url=path, headers=headers, data=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGALU_API > __refresh_token() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def __orders(self, order_number:str) -> requests.Response | dict:
        """ Recurso para consultar parcialmente um ou mais pedidos, com opçãos de parametros na consulta. """

        try:
            path = f'{self.api_production_environment}/v{self.api_version}/orders?code__in={order_number.replace("LU-", "")}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGALU_API > __orders() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}


    @__check_api_call
    def __orders_id(self, order_id:str) -> requests.Response | dict:
        """ Recurso para acessar um único pedido específico. """

        try:
            path = f'{self.api_production_environment}/v{self.api_version}/orders/{order_id}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGALU_API > __orders_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}


    @__check_api_call
    def __portfolios_skus(self, product_sku:str) -> requests.Response | dict:
        """ Recurso para consultar parcialmente um ou mais produtos com opções de parametros na consulta, buscando pelo sku do produto. """

        try:
            path = f'{self.api_production_environment}/v{self.api_version}/portfolios/skus?code__in={product_sku}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGALU_API > __portfolios_skus() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}


    @__check_api_call
    def __portfolios_skus_id(self, product_id:str) -> requests.Response | dict:
        """ Recurso para consultar um único produto específico, buscando pelo ID. """

        try:
            path = f'{self.api_production_environment}/v{self.api_version}/portfolios/skus/{product_id}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGALU_API > __portfolios_skus_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, ordem_number:str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            def_order_id = self.__orders(ordem_number)
            set_order = self.__orders_id(def_order_id['results'][0]['id'])

            for response in [def_order_id, set_order]:
                if "Error" in response:
                    return response

            return {
                "orderDate": datetime.fromisoformat(set_order['created_at']).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": f'LU-{set_order['code']}',
                "orderReference": None,
                "orderChannel": "Magazine Luiza",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": f'{set_order['agreement']['buyer']['extras']['name']}'.title(),
                "customerID": None,
                "customerNickname": None,
                "customerPhone": None,
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_order['agreement']['recipients'][0]['address']['street']}, n{set_order['agreement']['recipients'][0]['address']['number']}, {set_order['agreement']['recipients'][0]['address']['complement'] if set_order['agreement']['recipients'][0]['address']['complement'] != None else ""} {set_order['agreement']['recipients'][0]['address']['reference'] if set_order['agreement']['recipients'][0]['address']['reference'] != None else ""}, {set_order['agreement']['recipients'][0]['address']['district']}, {set_order['agreement']['recipients'][0]['address']['city']}, {set_order['agreement']['recipients'][0]['address']['state']}, CEP: {set_order['agreement']['recipients'][0]['address']['zipcode']} - Quem Recebe: {set_order['agreement']['buyer']['extras']['name']}',

                    "endereco": set_order['agreement']['recipients'][0]['address']['street'],

                    "numero": set_order['agreement']['recipients'][0]['address']['number'],

                    "complemento": f'{set_order['agreement']['recipients'][0]['address']['complement'] if set_order['agreement']['recipients'][0]['address']['complement'] != None else ""} {set_order['agreement']['recipients'][0]['address']['reference'] if set_order['agreement']['recipients'][0]['address']['reference'] != None else ""}',

                    "bairro": set_order['agreement']['recipients'][0]['address']['district'],

                    "cidade": set_order['agreement']['recipients'][0]['address']['city'],

                    "uf": set_order['agreement']['recipients'][0]['address']['state'],

                    "cep": set_order['agreement']['recipients'][0]['address']['zipcode'],

                    "destinatario": set_order['agreement']['buyer']['extras']['name'],

                },
                "shippingMethod": None,
                "shippingDate": None,
                "original_shippingDate": None,
                "shippingTracking": None,
                "Products": [self.__product_patterns(product_sku=item["sku"]["code"], product_qtd=item["quantity"]) for item in set_order['agreement']["items"]]
            }

        except Exception as exc:
            print(f'\n❌ MAGALU_API > order_pattern() ==> EXCEPTION: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}


    def __product_patterns(self, product_sku:str, product_qtd:str) -> dict | None:
        """ Padroniza as informações do produto para importação no sistema. """

        try:
            def_product_id = self.__portfolios_skus(product_sku)
            set_product = self.__portfolios_skus_id(def_product_id["results"][0]["id"])

            for response in [def_product_id, set_product]:
                if "Error" in response:
                    return None

            return {
                "id": set_product['id'],
                "produto": set_product['title']['pt_BR'],
                "sku": set_product["code"],
                "qtd": int(product_qtd),
                "icon": set_product['medias'][0]['reference'],
                "personalizacao": f'{set_product['attributes']["variant"][0]['name']} {set_product['attributes']["variant"][0]['value']}' if len(set_product['attributes']["variant"]) != 0 else ""
            }

        except Exception as exc:
            print(f'\n❌ MAGALU_API > __product_patterns() ==> EXCEPTION: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------

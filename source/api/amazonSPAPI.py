import requests, json
from datetime import datetime
from pytz import timezone
from source.api.api import API


class AmazonSPAPI(API):

    """
    Classe para gerenciamento e controle da integração com a API da Amazon.

    Cada método abaixo representa um recurso da api disponibilizado pela Amazon,
    com excessão dos métodos terminados em "pattern". Esses, são métodos que
    padroniza a resposta da chamada para uso adequado no sistema.

    """

    def __init__(self, developer_account:str) -> None:
        super().__init__(developer_account, api_platform="Amazon")
        self.get_access()

        self.headers = {
            'x-amz-access-token': self.access_token,
            'Content-Type': 'application/json',
            'User-Agent': 'Fadrix SYS/4.0 (Language=Python/3.12.2; Platform=Windows/11)'
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

                    print(f'\n🐞 AMAZON_SPAPI > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text if call.__name__ != 'getCatalogItem' else str(json.loads(request_call.text))}\n') ##DEBUG
                    deserialize_response = json.loads(request_call.text)

                    if "errors" in deserialize_response:
                        match deserialize_response['errors'][0]['details']:

                            case 'The access token you provided has expired.' | 'The access token you provided is revoked, malformed or invalid.' | "Access token is missing in the request header.":
                                self.__auth_refresh_token()
                                request_attempts +=1
                                continue

                            case _:
                                return {"Error": {"Code": "CALL_ERROR", "Message": "Houve um erro na resposta da API, tente novamente ou consulte o suporte do sistema."}}

                    break

                if call.__name__ == '__auth_refresh_token':
                    self.update_access(
                        new_access_token=deserialize_response['access_token'],
                        new_refresh_token=deserialize_response['refresh_token']
                    )
                    self.headers['x-amz-access-token'] = deserialize_response['access_token']
                    return None

                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## AUTHORIZATION PROCESS ------

    @__check_api_call
    def __auth_refresh_token(self) -> requests.Response | None:
        """ Renova o token de acesso para chamadas da API. """

        try:
            path = 'https://api.amazon.com/auth/o2/token'
            payload = f'grant_type=refresh_token&refresh_token={self.access_token_refresh}&client_id={self.app_id}&client_secret={self.app_key}'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            request_resource = requests.request("POST", path, headers=headers, data=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > __auth_refresh_token() == EXCEPTION: {exc}\n')
            return None

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def getOrder(self, number_order:str) -> requests.Response | None:
        """ Retorna o pedido que você especificar. """

        try:
            path = f'{self.api_production_environment}/orders/v0/orders/{number_order}'
            request_resource = requests.request("GET", path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > __getOrder() == EXCEPTION: {exc}\n')
            return None


    @__check_api_call
    def getOrder_buyerInfo(self, number_order:str) -> requests.Response | None:
        """ Retorna informações do comprador para o pedido que você especificar. """

        try:
            path = f'{self.api_production_environment}/orders/v0/orders/{number_order}/buyerInfo'
            request_resource = requests.request("GET", path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > __getOrder_buyerInfo() == EXCEPTION: {exc}\n')
            return None


    @__check_api_call
    def getOrder_address(self, number_order:str) -> requests.Response | None:
        """ Retorna o endereço de entrega do pedido que você especificar. """

        try:
            path = f'{self.api_production_environment}/orders/v0/orders/{number_order}/address'
            request_resource = requests.request("GET", path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > __getOrder_address() == EXCEPTION: {exc}\n')
            return None


    @__check_api_call
    def getOrder_orderItems(self, number_order:str)  -> requests.Response | None:
        """ Retorna informações detalhadas do item do pedido para o pedido que você especificar. Se NextToken for fornecido, ele será usado para recuperar a próxima página de itens do pedido.

        Observação: quando um pedido está no estado Pendente (o pedido foi feito, mas o pagamento não foi autorizado), a operação getOrderItems não retorna informações sobre preços, impostos, taxas de envio, status de presente ou promoções para os itens do pedido no pedido. Depois que um pedido sai do estado Pendente (isso ocorre quando o pagamento foi autorizado) e entra no estado Não Enviado, Parcialmente Enviado ou Enviado, a operação getOrderItems retorna informações sobre preços, impostos, taxas de envio, status de presente e promoções para os itens do pedido no pedido.
        """

        try:
            path = f'{self.api_production_environment}/orders/v0/orders/{number_order}/orderItems'
            request_resource = requests.request("GET", path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > __getOrder_orderItems() == EXCEPTION: {exc}\n')
            return None


    @__check_api_call
    def getCatalogItem(self, product_asin:str, marketplaceId:str)  -> requests.Response | None:
        """ Recupera detalhes de um item no catálogo da Amazon. """

        #_SL75_.jpg aumentar a imagem mudando para => _SL500_.jpg

        try:
            path = f'{self.api_production_environment}/catalog/v0/items/{product_asin}?MarketplaceId={marketplaceId}'
            request_resource = requests.request("GET", path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > __getCatalogItem() == EXCEPTION: {exc}\n')
            return None


    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, ordem_number:str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            set_order = self.__getOrder(ordem_number)

            if "Error" in set_order:
                return set_order

            return {
                "orderDate": datetime.fromisoformat(None).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": None,
                "orderReference": None,
                "orderChannel": "Amazon",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": None,
                "customerID": None,
                "customerNickname": None,
                "customerPhone": None,
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_order['street']}, n{set_order['number']}, {set_order['complement']}, {set_order['district']}, {set_order['city']}, {set_order['state']}, CEP: {set_order['zipcode']} - Quem Recebe: {set_order['name']}',

                    "endereco": set_order['street'],

                    "numero": set_order['number'],

                    "complemento": f'{set_order['complement']}',

                    "bairro": set_order['agreement']['district'],

                    "cidade": set_order['city'],

                    "uf": set_order['state'],

                    "cep": set_order['zipcode'],

                    "destinatario": set_order['name'],

                },
                "shippingMethod": None,
                "shippingDate": None,
                "original_shippingDate": None,
                "shippingTracking": None,
                "Products": None
            }

        except Exception as exc:
            print(f'\n❌ AMAZON_SPAPI > order_pattern() ==> EXCEPTION: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------
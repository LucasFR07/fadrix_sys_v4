import requests, json
from datetime import datetime
from pytz import timezone
from source.api.api import API


class Magis5(API):

    """
    Classe para gerenciamento e controle da integração com a API do Magis5.

    Cada método abaixo representa um recurso da api disponibilizado pela Magis5,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****


    magis5hub_status = {
        'awaiting_payment': 'Aguardando pagamento',
        'awaiting_approval': 'Aguardando Aprovação',
        'approved': 'Aprovado',
        'processing_pack_id': 'Processando carrinho',
        'out_of_stock': 'Sem estoque',
        'awaiting_stock': 'Aguardando reposição estoque',
        'awaiting_logistic': 'Aguardando logística',
        'ready_to_print': 'Aguardando separação',
        'awaiting_invoice': 'Aguardando faturamento',
        'billed': 'Faturado',
        'awaiting_send': 'Aguardando envio',
        'sent': 'Enviado',
        'delivered': 'Entregue',
        'delivered_resolved': 'Entregue e resolvido',
        'not_delivered': 'Não entregue',
        'not_delivered_resolved': 'Não entregue e resolvido',
        'canceled': 'Cancelado',
        'canceled_resolved': 'Cancelado e resolvido',
        'returned_logistic': 'Devolução Logística'
    }

    """




    def __init__(self) -> None:
        super().__init__(developer_account=None, api_platform="Magis5HUB")
        self.get_access()

        self.headers = {
            'accept': 'application/json',
            'X-MAGIS5-APIKEY': f'{self.access_token}',
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

                    print(f'\n🐞 MAGIS5_HUB > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG

                    match request_call.status_code:

                        case 200: #Ok
                            break

                        case 201: #Create
                            break

                        case 400: #Requisição inválida, verifique JSON.
                            deserialize_response = json.loads(request_call.text)
                            return {"Error": {"Code": "INVALID_REQUEST", "Message": deserialize_response["error"]}}

                        case 401: #Unauthorized.
                            return {"Error": {"Code": "INVALID_TOKEN", "Message": "X-MAGIS5-APIKEY is invalid"}}

                        case 404: #NotFound
                            return {"Error": {"Code": "NOT_FOUND", "Message": "Pedido não encontrado no Magis5, verifique o número informado,\n ou para MercadoLivre verifique a opção de carrinho."}}

                        case 500 | 502 | 503: #ServerError
                            return {"Error": {"Code": "SERVER_FALL", "Message": "Falha no servidor (API) do Magis5, não está respondendo no momento. Aguarde alguns instantes e tente novamente."}}

                        case _:
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API Magis5, consulte o suporte do sistema."}}

                deserialize_response = json.loads(request_call.text)
                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## RECURSOS DA API ------

    @__check_api_call
    def get_list_channels(self) -> requests.Response | None:
        """ Retorna lista de canais de venda integrado. """

        try:
            path = f'{self.api_production_environment}/v1/channels?limit=50&page=1&enableLink=true'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > __get_list_channels() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def get_orders(self, order_number:str) -> requests.Response | None:
        """ Retorna um pedido em específico. """

        try:
            path = f'{self.api_production_environment}/v1/orders/{order_number}?enableLink=true'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > get_orders() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def create_order(self, order_json:dict) -> requests.Response | None:
        """ Cria um novo pedido. """

        try:
            path = f'{self.api_production_environment}/v1/orders'
            request_resource = requests.post(url=path, headers=self.headers, json=order_json)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > __create_order() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def update_order(self, order_number:str, order_json:dict) -> requests.Response | None:
        """ Atualiza apenas alguns campos do pedido. """

        try:
            path = f'{self.api_production_environment}/v1/orders/{order_number}'
            request_resource = requests.patch(url=path, headers=self.headers, json=order_json)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > update_order() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def create_product(self, product_json:dict) -> requests.Response | None:
        """ Cria um novo pedido. """

        try:
            path = f'{self.api_production_environment}/v1/products'
            request_resource = requests.post(url=path, headers=self.headers, json=product_json)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > create_product() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def get_product(self, sku:dict) -> requests.Response | None:
        """ Obtem informações de um produto. """

        try:
            path = f'{self.api_production_environment}/v1/products/{sku}?enableLink=true'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > get_product() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None
        
    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, order_number:str) -> dict | None:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            get_order = self.get_orders(order_number=order_number)

            if "Error" in get_order:
                return get_order

            return {
                "orderDate": datetime.fromisoformat(get_order["dateCreated"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": get_order["externalId"],
                "orderReference": None,
                "orderChannel": get_order["channelName"].split("-")[0].strip(),
                "orderChannelID": get_order["channel"],
                "orderCompany": get_order["channelName"].split("-")[2].strip(),
                "customer": get_order["buyer"]["full_name"].title(),
                "customerID": get_order["buyer"]["id"],
                "customerNickname": get_order["buyer"]["nickname"],
                "customerPhone": get_order["buyer"]["phone"]["number"],
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{get_order["shipping"]["receiver_address"]["street_name"]}, n{get_order["shipping"]["receiver_address"]["street_number"]}, {get_order["shipping"]["receiver_address"]["comment"]}, {get_order["shipping"]["receiver_address"]["neighborhood"]["name"]}, {get_order["shipping"]["receiver_address"]["city"]["name"]}, {get_order["shipping"]["receiver_address"]["state"]["name"]}, CEP: {get_order["shipping"]["receiver_address"]["zip_code"]} - Quem Recebe: {get_order["shipping"]["receiver_address"]["name"].title()}',

                    "endereco": get_order["shipping"]["receiver_address"]["street_name"],

                    "numero": get_order["shipping"]["receiver_address"]["street_number"],

                    "complemento": get_order["shipping"]["receiver_address"]["comment"],

                    "bairro": get_order["shipping"]["receiver_address"]["neighborhood"]["name"],

                    "cidade": get_order["shipping"]["receiver_address"]["city"]["name"],

                    "uf": get_order["shipping"]["receiver_address"]["state"]["name"],

                    "cep": get_order["shipping"]["receiver_address"]["zip_code"],

                    "destinatario": get_order["shipping"]["receiver_address"]["name"].title()

                },
                "shippingMethod": None,
                "shippingDate": None,
                "original_shippingDate": None,
                "shippingTracking": None,
                "Products": [
                    {
                        "id": item["item"]["id"],
                        "produto": item["item"]["title"],
                        "sku": item["item"]["seller_custom_field"],
                        "qtd": item["quantity"],
                        "icon": item["item"]["defaultPicture"],
                        "personalizacao": ""
                    } for item in get_order["order_items"]
                ]
            }

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > order_pattern() ==> EXCEPTION: {exc}\n')
            return None


    def set_orderStatus(self, status:str) -> dict | None:
        """ Retorna o stats do pedido de acordo com o código informado. """

        try:
            magis5hub_status = {
                'awaiting_payment': 'Aguardando pagamento',
                'awaiting_approval': 'Aguardando Aprovação',
                'approved': 'Aprovado',
                'processing_pack_id': 'Processando carrinho',
                'out_of_stock': 'Sem estoque',
                'awaiting_stock': 'Aguardando reposição estoque',
                'awaiting_logistic': 'Aguardando logística',
                'ready_to_print': 'Aguardando separação',
                'awaiting_invoice': 'Aguardando faturamento',
                'billed': 'Faturado',
                'awaiting_send': 'Aguardando envio',
                'sent': 'Enviado',
                'delivered': 'Entregue',
                'delivered_resolved': 'Entregue e resolvido',
                'not_delivered': 'Não entregue',
                'not_delivered_resolved': 'Não entregue e resolvido',
                'canceled': 'Cancelado',
                'canceled_resolved': 'Cancelado e resolvido',
                'returned_logistic': 'Devolução Logística'
            }

            if status in magis5hub_status:
                return magis5hub_status[status]

            return None

        except Exception as exc:
            print(f'\n❌ MAGIS5_HUB > set_orderStatus() ==> EXCEPTION: {exc}\n')
            return None

    ## ------

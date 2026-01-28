import requests, json
from datetime import datetime
from pytz import timezone
from source.api.api import API


class IderisV3(API):

    """
    Classe para gerenciamento e controle da integração com a API do Ideris V3.

    Cada método abaixo representa um recurso da api disponibilizado pela Ideris V3,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self) -> None:
        super().__init__(developer_account=None, api_platform="Ideris")
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

                    print(f'\n🐞 IDERIS_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG

                    match request_call.status_code:

                        case 200: #Ok
                            break

                        case 204: #NotFound
                            return {"Error": {"Code": "NOT_FOUND", "Message": "Pedido não encontrado no IDERIS, verifique o número informado,\n ou para MercadoLivre verifique a opção de carrinho."}}

                        case 401: #Unauthorized.
                            self.__login()
                            request_attempts +=1
                            continue

                        case 500: #ServerError
                            return {"Error": {"Code": "SERVER_FALL", "Message": "Falha no servidor (API) do Ideris, não está respondendo no momento. Aguarde alguns instantes e tente novamente."}}

                        case _:
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API Ideris, consulte o suporte do sistema."}}

                if call.__name__ == "__login":
                    self.update_only_access_token(new_access_token=request_call.text)
                    self.headers['Authorization'] = f'Bearer {request_call.text}'
                    return None

                deserialize_response = json.loads(request_call.text)
                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ IDERIS_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## AUTHORIZATION PROCESS ------

    @__check_api_call
    def __login(self) -> requests.Response | None:
        """ O objetivo deste end point é a criação de um token JWT para ser possível utilizar os outros end points da API V3 Ideris. """

        try:
            path = f'{self.api_production_environment}/login'
            payload = json.dumps(self.access_code)
            headers = {'Content-Type': 'application/json'}

            request_resource = requests.post(url=path, headers=headers, data=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ IDERIS_API > __login() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def settings_marketplace(self) -> requests.Response | None:
        """ Consulta da lista de marketplaces integrados no Ideris. """

        try:
            path = f'{self.api_production_environment}/settings/marketplace'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ IDERIS_API > __settings_marketplace() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def get_idAuthentication(self, idAuthentication:int) -> requests.Response | None:
        """ Consulta da lista de marketplaces integrados no Ideris. """

        try:
            path = f'{self.api_production_environment}/authentication/{idAuthentication}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ IDERIS_API > get_idAuthentication() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __settings_marketplace_id(self, marketplace_id:str) -> requests.Response | None:
        """ Consulta de marketplace integrado no Ideris pelo ID. """

        try:
            path = f'{self.api_production_environment}/settings/marketplace/{marketplace_id}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ IDERIS_API > __settings_marketplace_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __order_search(self, order_number:str, pack:bool=False) -> requests.Response | None:
        """ Consulta de lista de pedidos por filtros. """

        try:
            search_param = f'orderCode={order_number}' if not pack else f'orderPackId={order_number}'

            path = f'{self.api_production_environment}/order/search?{search_param}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ IDERIS_API > __order_search() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __order_id(self, order_id:str) -> requests.Response | None:
        """ Consulta de pedido por ID. """

        try:
            path = f'{self.api_production_environment}/order/{order_id}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ IDERIS_API > __order_id() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def create_order(self, order_data:dict) -> requests.Response | None:
        """ Cria um novo pedido no Ideris. """

        try:
            path = f'{self.api_production_environment}/order'
            request_resource = requests.post(url=path, headers=self.headers, data=order_data)
            return request_resource

        except Exception as exc:
            print(f'\n❌ IDERIS_API > __create_order() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, order_number:str, pack_order:bool=False) -> dict | None:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            get_order_ideris_id = self.__order_search(order_number=order_number, pack=pack_order)

            if "Error" in get_order_ideris_id:
                return get_order_ideris_id

            products_list = list()
            set_objID_list = list()

            for order in get_order_ideris_id['obj']:

                if order['id'] in set_objID_list:
                    continue

                set_order = self.__order_id(order_id=order['id'])

                if "Error" in set_order:
                    return set_order

                if set_order["obj"]["packId"] != None and order_number != set_order["obj"]["packId"]:
                    return {"Error": {"Code": "PACK_ORDER", "Message": "Pedido de Carrinho MercadoLivre. Favor, refazer a busca pelo número do carrinho."}}

                for item in set_order['obj']["items"]:
                    products_list.append(
                        {
                            "id": item["codeProduct"],
                            "produto": item["title"],
                            "sku": item["sku"],
                            "qtd": item["quantity"],
                            "icon": item["image"],
                            "personalizacao": ", ".join([f'{va["name"]}: {va["value"]}' for va in item["productVariation"]]) if len(item["productVariation"]) != 0 else ""
                        }
                    )

                set_objID_list.append(order['id'])

            return {
                "orderDate": datetime.fromisoformat(set_order['obj']["created"]).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": set_order['obj']["code"] if not pack_order else order_number,
                "orderReference": None,
                "orderChannel": set_order['obj']["originName"] if set_order['obj']["originName"].find("-") == -1 else set_order['obj']["originName"].split("-")[1].replace(" ", "", 1),
                "orderChannelID": set_order['obj']["authenticationId"],
                "orderCompany": None,
                "customer": f'{set_order['obj']["customerFirstName"]} {set_order['obj']["customerLastName"]}'.title(),
                "customerID": None,
                "customerNickname": None,
                "customerPhone": set_order['obj']["addressReceiverPhone"],
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_order['obj']["addressStreet"]}, n{set_order['obj']["addressNumber"]}, {set_order['obj']["addressComment"]}, {set_order['obj']["districtName"]}, {set_order['obj']["cityName"]}, {set_order['obj']["stateName"]}, CEP: {set_order['obj']["addressZipCode"]} - Quem Recebe: {set_order['obj']["addressReceiverName"]}',

                    "endereco": set_order['obj']["addressStreet"],

                    "numero": set_order['obj']["addressNumber"],

                    "complemento": set_order['obj']["addressComment"],

                    "bairro": set_order['obj']["districtName"],

                    "cidade": set_order['obj']["cityName"],

                    "uf": set_order['obj']["stateName"],

                    "cep": set_order['obj']["addressZipCode"],

                    "destinatario": set_order['obj']["addressReceiverName"]

                },
                "shippingMethod": None,
                "shippingDate": None,
                "original_shippingDate": None,
                "shippingTracking": None,
                "Products": products_list
            }

        except Exception as exc:
            print(f'\n❌ IDERIS_API > order_pattern() ==> EXCEPTION: {exc}\n')
            return None

    ## ------



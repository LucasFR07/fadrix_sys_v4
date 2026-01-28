import requests, json
from datetime import datetime
from pytz import timezone
from source.api.api import API


class MagaluV1(API):

    """
    Classe para gerenciamento e controle da integração com a API da MAGALU.

    Cada método abaixo representa um recurso da api disponibilizado pela MAGALU,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    __CLASS_NAME = "MAGALU_API_V1"

    def __init__(self, developer_account:str) -> None:
        super().__init__(developer_account, api_platform="Magazine Luiza")
        self.get_access()

        self.call_header = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'X-Channel-Id': '9fe0d853-732b-4e4a-a0b0-cff988ed043d'
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

                    print(f'\n[DEBUG] {__class__.__CLASS_NAME} > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG
                    
                    match request_call.status_code:

                        case 403:
                            # Tentar ler a resposta para mais detalhes
                            try:
                                error_response = json.loads(request_call.text)
                                error_msg = error_response.get("message", error_response.get("error", error_response.get("developerMessage", "Acesso negado")))
                                print(f'\n[ERRO] {__class__.__CLASS_NAME} > CHECK_CALL > {call.__name__}() ==> 403 FORBIDDEN\n')
                                print(f'Resposta completa: {request_call.text}\n')
                                return {"Error": {"Code": "FORBIDDEN", "Message": f"Acesso negado: {error_msg}. Verifique as permissões da API e o número do pedido."}}
                            except Exception as e:
                                print(f'\n[ERRO] {__class__.__CLASS_NAME} > CHECK_CALL > {call.__name__}() ==> 403 FORBIDDEN (sem JSON)\n')
                                print(f'Resposta: {request_call.text}\n')
                                return {"Error": {"Code": "FORBIDDEN", "Message": "Acesso negado. Verifique as permissões da API e o número do pedido."}}

                        case 404:
                            try:
                                error_response = json.loads(request_call.text)
                                error_msg = error_response.get("message", "Pedido não encontrado")
                                return {"Error": {"Code": "NOT_FOUND", "Message": f"Pedido não encontrado: {error_msg}"}}
                            except:
                                return {"Error": {"Code": "NOT_FOUND", "Message": "Pedido não encontrado. Verifique o número do pedido."}}

                        case 200 | 201:
                            # Sucesso, continuar processamento
                            pass

                        case _:
                            # Outros status codes - tentar processar normalmente
                            pass
                    
                    deserialize_response = json.loads(request_call.text)

                    # Verificar se há erro na resposta
                    if "error" in deserialize_response:
                        if deserialize_response["error"] == "invalid_grant":
                            print(f'\n[ERRO] {__class__.__CLASS_NAME} > CHECK_CALL > {call.__name__}() ==> REFRESH TOKEN EXPIRADO. Necessário gerar novo authorization_code.\n')
                            return {"Error": {"Code": "TOKEN_EXPIRED", "Message": "Token de atualização expirado. É necessário realizar nova autorização."}}
                        else:
                            return {"Error": {"Code": "API_ERROR", "Message": f"Erro na API: {deserialize_response.get('error_description', 'Erro desconhecido')}"}}

                    if "developerMessage" in deserialize_response:
                        match deserialize_response["developerMessage"]:

                            case 'Unauthorized':
                                refresh_result = self.__refresh_token()
                                if refresh_result and "Error" in refresh_result:
                                    return refresh_result
                                request_attempts +=1
                                continue

                            case _:
                                return {"Error": {"Code": "CALL_ERROR", "Message": "Houve um erro na resposta da API, tente novamente ou consulte o suporte do sistema."}}

                    break

                if call.__name__ in ["__authorization_code", "authorization_code", "__refresh_token", "refresh_token"]:
                    if "access_token" in deserialize_response and "refresh_token" in deserialize_response:
                        self.update_access(
                            new_access_token = deserialize_response["access_token"],
                            new_refresh_token = deserialize_response["refresh_token"]
                        )
                        self.call_header['Authorization'] = f'Bearer {deserialize_response["access_token"]}'
                    return None

                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ {__class__.__CLASS_NAME} > __check_api_call() == EXCEPTION: {exc}\n')
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
            print(f'\n❌ {__class__.__CLASS_NAME} > authorization_code() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
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
            print(f'\n[ERRO] {__class__.__CLASS_NAME} > __refresh_token() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def __get_orders(self, order_number:str) -> requests.Response | dict:
        """ Recurso para consultar parcialmente um ou mais pedidos, com opçãos de parametros na consulta. """

        try:
            path = f'{self.api_production_environment}/seller/v1/orders?code={order_number.replace("LU-","")}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n[ERRO] {__class__.__CLASS_NAME} > __get_orders() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            import traceback
            traceback.print_exc()
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}


    @__check_api_call
    def __get_deliveries(self, order_number:str) -> requests.Response | dict:
        """ Recurso para consultar parcialmente um ou mais pedidos, com opçãos de parametros na consulta. """

        try:
            path = f'{self.api_production_environment}/seller/v1/deliveries?code={order_number.replace("LU-","")}'
            request_resource = requests.get(url=path, headers=self.call_header)
            return request_resource

        except Exception as exc:
            print(f'\n❌ {__class__.__CLASS_NAME} > __get_deliveries() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------



    ## MÉTODOS DO SISTEMA ------

    def order_pattern(self, ordem_number:str) -> dict:
        """ Padroniza as informações do pedido para importação no sistema. """

        try:
            set_order = self.__get_orders(ordem_number)

            if set_order is None:
                return {"Error": {"Code": "EXCEPTION", "Message": "Erro ao buscar pedido. Verifique o número do pedido e tente novamente."}}
            
            if "Error" in set_order:
                return set_order

            shipping_address_complement = set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["complement"] if "complement" in set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"] else " - "

            shipping_address_reference = set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["reference"] if "reference" in set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"] else " - "

            shipping_address__complement_reference = f'{shipping_address_complement}, REF. {shipping_address_reference}'.title()

            return {
                "orderDate": datetime.fromisoformat(set_order["results"][0]['created_at']).astimezone(tz=timezone('America/Sao_Paulo')),
                "orderNumber": f'LU-{set_order["results"][0]['code']}',
                "orderReference": None,
                "orderChannel": "Magazine Luiza",
                "orderChannelID": None,
                "orderCompany": self.developer_account,
                "customer": f'{set_order["results"][0]["customer"]['name']}'.title(),
                "customerID": None,
                "customerNickname": None,
                "customerPhone": None,
                "order_customerEmail": None,
                "shippingAddress": {

                    "enderecoCompleto": f'{set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["street"].title()}, n{set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["number"]}, {shipping_address__complement_reference}, {set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["district"].title()}, {set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["city"].title()}, {set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["state"]}, CEP: {set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["zipcode"]} - Quem Recebe: {set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["name"].title()}',

                    "endereco": set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["street"].title(),

                    "numero": set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["number"].title(),

                    "complemento": shipping_address__complement_reference,

                    "bairro": set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["district"].title(),

                    "cidade": set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["city"].title(),

                    "uf": set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["state"],

                    "cep": set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["address"]["zipcode"],

                    "destinatario": f'{set_order["results"][0]["deliveries"][0]["shipping"]["recipient"]["name"]}'.title(),

                },
                "shippingMethod": None,
                "shippingDate": None,
                "original_shippingDate": None,
                "shippingTracking": None,
                "Products": [
                    {
                        "id": product["info"]['id'],
                        "produto": product["info"]["name"],
                        "sku": product["info"]["sku"],
                        "qtd": product["quantity"],
                        "icon": product["info"]["images"][0]["url"],
                        "personalizacao": None,
                    }                        

                for product in set_order["results"][0]["deliveries"][0]["items"]
                ],
            }

        except Exception as exc:
            print(f'\n[ERRO] {__class__.__CLASS_NAME} > order_pattern() ==> EXCEPTION: {exc}\n')
            import traceback
            traceback.print_exc()
            return {"Error": {"Code": "EXCEPTION", "Message": "Houve um erro interno, tente novamente ou consulte o suporte do sistema."}}

    ## ------

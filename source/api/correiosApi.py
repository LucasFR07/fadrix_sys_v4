import requests, json, base64
from datetime import datetime
from pytz import timezone
from source.api.api import API


class Correios(API):
    """
    Classe para gerenciamento e controle da integração com a API Correios.

    Cada método abaixo representa um recurso da api disponibilizado pelo Correios,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """  

    def __init__(self) -> None:
        super().__init__(developer_account="FBF COMUNICACAO", api_platform="Correios API")
        self.get_access()

        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }

       # user_account == CNPJ
       # app_id == NUM. CARTÃO POSTAGEM
       # app_key == NUM. CONTRATO        



    def __check_api_call(call): ## DECORADOR DE CHECAGEM
        """ Verifica a chamada da API, padronizando e resolvendo retornos de erro. """

        try:
            def wrapper(self, *args, **kwargs):
                request_attempts = 1

                for _ in range(2):
                    request_call = call(self, *args, **kwargs)

                    if request_call == None:
                        return {"Error": {"Code": "INTERNAL_ERROR", "Message": "Houve um erro interno ao solicitar essa chamada, consulte o suporte do sistema."}}

                    print(f'\n🐞 CORREIOS_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG

                    match request_call.status_code:

                        case 200 | 201: #Ok
                            break

                        case 403: #Unauthorized.
                            self.__autentica_cartaopostagem()
                            request_attempts +=1
                            continue

                        case 500: #ServerError
                            return {"Error": {"Code": "SERVER_FALL", "Message": "Falha no servidor (API) dos Correios, não está respondendo no momento. Aguarde alguns instantes e tente novamente."}}

                        case _:
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API Correios, consulte o suporte do sistema."}}


                deserialize_response = json.loads(request_call.text)

                if call.__name__ == "__autentica_cartaopostagem":
                    self.update_only_access_token(new_access_token=deserialize_response["token"])
                    self.headers['Authorization'] = f'Bearer {deserialize_response["token"]}'
                    return None

                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ CORREIOS_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## AUTHORIZATION PROCESS ------

    @__check_api_call
    def __autentica_cartaopostagem(self) -> requests.Response | None:
        """
            Serviço de geração de token, para acesso a diversas APIs dos Correios.

            → Para solicitar um token é necessário fazer uma requisição com 'Authorization: Basic', passando o usuário (Meu Correios) e senha (código de acesso).
            → O token obtido tem uma data de expiração no atributo 'expiraEm', com isso o mesmo token pode ser utilizado até a data de expiração. Recomendamos que solicite um novo token próximo da data de expiração, alguns minutos antes do token expirar.
        """

        try:
            path = f'{self.api_production_environment}/token/v1/autentica/cartaopostagem'
            payload = json.dumps({"numero":self.app_id, "contrato":self.app_key, "dr":50})

            authorization_string = "%s:%s" % (self.login_user, self.login_passwd)
            authorization_encode = authorization_string.encode()

            headers = {
                'Authorization': f'Basic {base64.b64encode(authorization_encode).decode()}',
                'Content-Type': 'application/json',
            }

            request_resource = requests.post(url=path, headers=headers, data=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ CORREIOS_API > __autentica_cartaopostagem() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------



    ## RECURSOS DA API ------

    @__check_api_call
    def __servicos_cartaopostagem(self) -> requests.Response | None:
        """ Consulta os serviços disponíveis de um cartão de postagem. """

        try:
            path = f'{self.api_production_environment}/meucontrato/v1/empresas/{self.user_account}/contratos/{self.app_key}/cartoes/{self.app_id}/servicos'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ CORREIOS_API > __servicos_cartaopostagem() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __enderecos_cep(self, cep_number:str) -> requests.Response | None:
        """ Consulta de endereços por cep. """

        try:
            path = f'{self.api_production_environment}/cep/v2/enderecos/{cep_number}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ CORREIOS_API > __enderecos_cep() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def __servicos_adicionais(self, cod_servico:str) -> requests.Response | None:
        """ Consulta preços dos serviços adicionais de um produto. """

        try:
            path = f'{self.api_production_environment}/preco/v1/servicos-adicionais/{cod_servico}'
            request_resource = requests.post(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ CORREIOS_API > __servicos_adicionais() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def preco_nacional(self, cotacao_data:list) -> requests.Response | None:
        """ Consulta preços de uma lista de produtos. """

        try:
            path = f'{self.api_production_environment}/preco/v1/nacional'
            payload = {"idLote":"1231", "parametrosProduto":cotacao_data}

            request_resource = requests.post(url=path, headers=self.headers, json=payload)
            return request_resource

        except Exception as exc:
            print(f'\n❌ CORREIOS_API > preco_nacional() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def rastro_objetos(self, cod_objeto:str) -> requests.Response | None:
        """ Método para consultar os eventos de um determinado objeto. """

        try:
            path = f'{self.api_production_environment}/srorastro/v1/objetos/{cod_objeto}?resultado=T'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ CORREIOS_API > rastro_objetos() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------

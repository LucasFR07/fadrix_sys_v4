import requests, json
from pathlib import Path
from datetime import datetime
from pytz import timezone
from source.api.api import API


class AsanaAPI(API):

    """
    Classe para gerenciamento e controle da integração com a API do Asana.

    Cada método abaixo representa um recurso da api disponibilizado pelo Asana,
    com excessão dos métodos terminados em "pattern" e "rule", que são métodos para
    padronizar a resposta da chamada para uso adequado no sistema.

    @author: Douglas Leal <https://github.com/douleal>
    @copyright: 2024 Douglas Leal
    @license: ****
    """

    def __init__(self) -> None:
        super().__init__(developer_account=None, api_platform="Asana")
        self.get_access()

        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Acept': "application/json"
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

                    print(f'\n🐞 ASANA_API > CHECK_CALL 0{request_attempts} > {call.__name__}() ==> RESPONSE: {request_call.status_code} | {request_call.text}\n') ##DEBUG

                    match request_call.status_code:

                        case 200 | 201: #Successfully
                            break

                        case 500: #ServerError
                            return {"Error": {"Code": "SERVER_FALL", "Message": "Falha no servidor (API) do Asana, não está respondendo no momento. Aguarde alguns instantes e tente novamente."}}

                        case _:
                            return {"Error": {"Code": {request_call.status_code}, "Message": "Erro na resposta da API do Asana, consulte o suporte do sistema."}}


                deserialize_response = json.loads(request_call.text)
                return deserialize_response

            return wrapper

        except Exception as exc:
            print(f'\n❌ ASANA_API > __check_api_call() == EXCEPTION: {exc}\n')
            return None



    ## RECURSOS DA API ------

    @__check_api_call
    def get_a_user(self, user_gid:str) -> requests.Response | None:
        """ Retorna o registro completo do usuário para o usuário único com o ID fornecido. """

        try:
            path = f'{self.api_production_environment}/users/{user_gid}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > get_a_user() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def get_a_custom_fields(self, custom_field_gid:str) -> requests.Response | None:
        """ Obtenha a definição completa dos metadados de um campo personalizado.

        custom_field_gid = {
            "1202887017424348": "CANAL DE VENDA",
            "1204585380463794": "EMPRESA",
            "1202884793721450": "ATENDENTE",
            "1202996802045806": "FORMA DE ENVIO",
            "1211627442120662": "MOTIVO GARANTIA",            
        }

        """

        try:
            path = f'{self.api_production_environment}/custom_fields/{custom_field_gid}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > get_a_custom_fields() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def get_a_workspaces_custom_fields(self) -> requests.Response | None:
        """ Obtem todos os campos personalziados do workspace. """

        try:
            path = f'{self.api_production_environment}/workspaces/1128098916536904/custom_fields'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > get_a_workspaces_custom_fields() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def get_a_task(self, task_gid:str) -> requests.Response | None:
        """ Retorna o registro completo de uma única tarefa. """

        try:
            path = f'{self.api_production_environment}/tasks/{task_gid}'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > get_a_task() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def get_a_task_custom_fields(self, task_gid:str) -> requests.Response | None:
        """ Retorna apenas os campos personaliados de uma única tarefa. """

        try:
            path = f'{self.api_production_environment}/tasks/{task_gid}?opt_fields=custom_fields.display_value'
            request_resource = requests.get(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > get_a_task_custom_fields() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def create_a_task(self, data_object:dict) -> requests.Response | None:
        """ Cria uma nova tarefa. """

        try:
            path = f'{self.api_production_environment}/tasks'
            request_resource = requests.post(url=path, headers=self.headers, json=data_object)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > create_a_task() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def create_a_subtask(self, task_gid:str, data_object:dict) -> requests.Response | None:
        """ Cria uma nova subtarefa e a adiciona à tarefa pai. Retorna o registro completo para a subtarefa recém-criada. """

        try:
            path = f'{self.api_production_environment}/tasks/{task_gid}/subtasks'
            request_resource = requests.post(url=path, headers=self.headers, json=data_object)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > create_a_subtask() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def update_a_task(self, task_gid:str, data_object:dict) -> requests.Response | None:
        """ Uma tarefa específica existente pode ser atualizada fazendo uma solicitação PUT na URL para essa tarefa.
            Apenas os campos fornecidos no bloco de dados serão atualizados; quaisquer campos não especificados permanecerão inalterados.
        """

        try:
            path = f'{self.api_production_environment}/tasks/{task_gid}'
            request_resource = requests.put(url=path, headers=self.headers, json=data_object)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > get_a_task() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def delete_a_task(self, task_gid:str) -> requests.Response | None:
        """
        Uma tarefa específica existente pode ser excluída fazendo uma solicitação DELETE na URL para essa tarefa.
        Tarefas excluídas vão para a "lixeira" do usuário que faz a solicitação de exclusão.
        Tarefas podem ser recuperadas da lixeira dentro de um período de 30 dias; depois disso, elas são completamente removidas do sistema.
        Retorna um registro de dados vazio.
        """

        try:
            path = f'{self.api_production_environment}/tasks/{task_gid}'
            request_resource = requests.delete(url=path, headers=self.headers)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > delete_a_task() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def upload_an_attachment(self, task_gid:str, file_path:Path, is_img:bool=True) -> requests.Response | None:
        """ Este método carrega um anexo em um objeto e retorna o registro compacto para o objeto de anexo criado. """

        try:
            data_file = {"file": (file_path.name, open(f'{file_path.parent}/{file_path.name}', 'rb'), 'image/jpeg')} if is_img else {"file": (file_path.name, open(f'{file_path.parent}/{file_path.name}', 'rb'))}

            path = f'{self.api_production_environment}/tasks/{task_gid}/attachments'
            request_resource = requests.post(url=path, headers=self.headers, files=data_file)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > upload_an_attachment() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None


    @__check_api_call
    def create_a_story_on_a_task(self, task_gid:str, text:str, is_pinned:bool=False) -> requests.Response | None:
        """
        Adiciona uma história a uma tarefa. Este endpoint atualmente permite apenas que histórias de comentários sejam criadas.
        O comentário será criado pelo usuário autenticado no momento e registrado com carimbo de data/hora quando o servidor receber a solicitação.
        Retorna o registro completo da nova história adicionada à tarefa.
        """

        try:
            data_story = {"data": {"html_text": f'<body>{text}</body>', "is_pinned": is_pinned}}

            path = f'{self.api_production_environment}/tasks/{task_gid}/stories'
            request_resource = requests.post(url=path, headers=self.headers, json=data_story)
            return request_resource

        except Exception as exc:
            print(f'\n❌ ASANA_API > create_a_story_on_a_task() ==> EXCEPTION IN REQUEST RESOURCE: {exc}\n')
            return None

    ## ------

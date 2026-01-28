from source.api.asanaApi import AsanaAPI as ASANA
from datetime import datetime


class AsanaGet:

    def __init__(self, task:dict) -> None:
        self.task = task
        self.asana = ASANA()


    def __set_gids_task(self) -> list:
        """ Obtem apenas os valores dos gids de cada tarefa, e retorna em lista. """

        try:
            task_gid = list()
            for key, value in self.task.items():
                match isinstance(value, str):
                    case True:
                        task_gid.append(value)
                    case False:
                        for gid in value:
                            task_gid.append(gid) 

            return task_gid

        except Exception as exc:
            print(f'\n❌ ASANAGET > __set_gids_task == EXCEPTION: {exc}\n')
            return []


    def get_task(self) -> dict:

        try:
            list_gids = self.__set_gids_task()
            dict_task = dict()

            for gid in list_gids:
                get_task = self.asana.get_a_task(gid)
                if "Error" in get_task:
                    dict_task[gid] = {
                        "name": "NÃO FOI POSSÍVEL RECUPERAR A TAREFA (CONTATAR SUPORTE)",
                        "assignee": None,
                        "data_completed": None,
                        "completed": None,
                        "projects": None,
                        "status": None,
                        "gid": gid,
                        "link": f'https://app.asana.com/0/1202261188290666/{gid}',
                        "delet": True
                    }

                    return dict_task

                get_user = self.asana.get_a_user(get_task["data"]["assignee"]["gid"]) if get_task["data"]["assignee"] != None else None

                set_task_project = list()
                for project in get_task["data"]["memberships"]:
                    set_task_project.append(
                        {
                            "project_name": project["project"]["name"],
                            "section_name": project["section"]["name"]
                        }
                    )

                set_status = str()
                for fild in get_task["data"]["custom_fields"]:
                    if fild["gid"] == "1202857995568623":
                        set_status = fild["enum_value"]
                        break

                dict_task[gid] = {
                    "name": get_task["data"]["name"],
                    "assignee": {
                        "assignee_name": get_task["data"]["assignee"]["name"] if get_task["data"]["assignee"] != None else "Nenhum Reponsável",
                        "assignee_photo": get_user["data"]["photo"]["image_21x21"] if get_user != None and get_user["data"]["photo"] != None else 'assets/images/profile/profile_default.png'
                    },
                    "data_completed": datetime.strptime(get_task["data"]["due_on"], '%Y-%m-%d').strftime('%d/%m/%Y'),
                    "completed": get_task["data"]["completed"],
                    "projects": set_task_project,
                    "status": {
                        "name": set_status['name'] if set_status != None else "NULL",
                        "color": set_status["color"] if set_status != None else "#faaaaa"
                    },
                    "gid": gid,
                    "link": get_task["data"]["permalink_url"],
                    "delet": False
                }

            return dict_task

        except Exception as exc:
            print(f'\n❌ ASANAGET > get_task == EXCEPTION: {exc}\n')
            return None

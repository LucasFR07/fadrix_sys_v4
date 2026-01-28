from data.repository.orderV2 import OrderRepositoryV2 as ORDER
from data.repository.order_product import OrderProductRepository as PRODUCT
from data.repository.company import CompanyRepository as COMPANY
from data.repository.carrier import CarrierRepository as CARRIER
from data.repository.userV2 import UserV2Repository as USER
from data.repository.saleschannel import SalesChannelRepository as SALES

from controllers.task_control import TaskControl as TASK
from source.api.asanaApi import AsanaAPI as ASANA


class Asana_Off_Import:

    def __init__(self, order_list:list) -> None:
        self.order_list = order_list


    def __set_task_gid(self, fild_task:dict) -> list:
        """ Obtem apenas os valores dos gids da tarefa, e retorna em lista. """

        try:
            task_gid = list()
            for key, value in fild_task.items():
                match isinstance(value, str):
                    case True:
                        task_gid.append(value)
                    case False:
                        for gid in value:
                            task_gid.append(gid)

            print(f'\n🐞 ASANA_OFF_IMPORT > __set_order() ==> TASK GID: {task_gid} \n') ##DEBUG
            return task_gid

        except Exception as exc:
            print(f'\n❌ ASANA_OFF_IMPORT > __set_task_gid() ==> EXCEPTION: {exc}\n')
            return []


    def __set_order(self, order_number:str):
        """ Obtem os dados do pedido informado. """

        try:
            get_order = ORDER().filter_number(number=order_number)
            print(f'\n🐞 ASANA_OFF_IMPORT > __set_order() ==> ORDER DICT: {get_order.__dict__} \n') ##DEBUG
            return get_order.__dict__ if get_order != None else None

        except Exception as exc:
            print(f'\n❌ ASANA_OFF_IMPORT > __set_order() ==> EXCEPTION: {exc}\n')
            return None


    def create_task(self, remove_old_task:bool=False):
        """ Importa o pedido pro Asana criando uma tarefa. """

        try:

            hit_list = list()
            fault_list = list()

            for order in self.order_list:
                set_order = self.__set_order(order_number=order)

                if not set_order:
                    continue

                company = COMPANY().filter_name(set_order['order_company'])
                search_carrier = CARRIER().filter_name(set_order['order_shippingMethod'])
                attendant = USER().filter_name(set_order['order_userSystem'])

                search_channel = SALES().filter_all()
                for chn in search_channel:
                    if chn.name == set_order['order_channel'] and chn.company["name"] == set_order['order_company']:
                        channel = {"id": chn.asanaID, "name": chn.name}

                list_products = PRODUCT().filter_number(number=order)

                data = {
                    "completion_date": str(set_order['order_shippingDate'].date()),
                    "project": "arte_final",
                    "custom_fields": {
                        "channel": channel["id"],
                        "company": company.asanaID,
                        "attendant": attendant.asanaID,
                        "shippingMethod": search_carrier.asanaID
                    },
                    "info": {
                        "number": set_order['order_number'],
                        "customer": set_order['order_customer'],
                        "date": set_order['order_date'],
                        "channel": channel["name"],
                        "company": company.name,
                        "attendant": attendant.name,
                        "address": set_order['order_shippingAddress']['enderecoCompleto'],
                        "shippingMethod": search_carrier.name,
                        "products": [
                            {
                                "id": product.id,
                                "produto": product.name,
                                "sku": product.sku,
                                "qtd": product.qty,
                                "icon": product.icon if product.icon != None or product.icon != "" else "#",
                                "personalizacao": product.customization
                            } for product in list_products
                        ]
                    },
                    "comments": [{"text": set_order['order_historic'], "pinned" : False}]
                }

                try:
                    create_task = TASK().create(type_body="order", task_data=data)
                    ORDER().update(id=set_order['id'], fild="order_task", data={"gid": create_task["data"]["gid"]})
                    #print(f'\n🐞 ASANA_OFF_IMPORT > create_task() ==> PEDIDO #{set_order['order_number']} - {set_order['order_customer']} || ENVIADO P/ ASANA COM SUCESSO !!\n') ##DEBUG

                    hit_list.append(f'PEDIDO #{set_order['order_number']} - {set_order['order_customer']}')

                except:
                    fault_list.append(f'PEDIDO #{set_order['order_number']} - {set_order['order_customer']}')


            print(f'\n🐞 ASANA_OFF_IMPORT > create_task() ==> RELATÓRIO DE ENVIOS P/ ASANA:\n\n# ENVIADO COM SUCESSO: {len(hit_list)}\n{'\n  →'.join(hit_list)}\n\n# ENVIO COM FALHA: {len(fault_list)}\n{'\n  →'.join(fault_list)}') ##DEBUG


        except Exception as exc:
            print(f'\n❌ ASANA_OFF_IMPORT > create_task() ==> EXCEPTION: {exc}\n')
            return None

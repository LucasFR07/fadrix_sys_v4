import math, tablib
import pandas as pd
from datetime import datetime
from source.api.asanaApi import AsanaAPI
from data.repository.orderV2 import OrderRepositoryV2 as ORDER
from data.repository.order_product import OrderProductRepository as PRODUCT


class Shein_AutoExcel:

    CLASS_NAME = "SHEIN_AUTOEXCEL"

    def __init__(self, path:str):
        self.path_file = path


    def get_order_list(self, only_number:bool=False, set_group:bool=False) -> list:
        """ Obtem uma listagem com números dos pedidos. """

        try:
            order_list = list()
            order_list_only_number = list()

            read_excel = pd.read_excel(self.path_file, usecols=['Número do pedido', 'Data e hora requeridas para coleta'])
            remove_duplicate = read_excel.drop_duplicates()
            print(f'\n🐞 GET_ORDER_LIST ==> READ_EXCEL: {remove_duplicate}\n')

            for order in remove_duplicate.values.tolist():
                if not set_group:
                    # if str(order[1])[:2] == '20': ## FILTRAR POR DATA ESPECÍFICA
                    if str(order[1])[:2] == str(datetime.today().day).zfill(2):
                        print(f'\n🐞 GET_ORDER_LIST ==> FOR ORDER IF "DATA COLETA" == TODAY: {order}\n')
                        order_list.append(order)
                        order_list_only_number.append(order[0])
                else:
                    order_list.append(order)
                    order_list_only_number.append(order[0])                    

            print(f'\n🐞 GET_ORDER_LIST ==> TOTAL PEDIDOS: {len(order_list)}\n')
            print(f'\n🐞 GET_ORDER_LIST ==> PEDIDOS: {order_list}\n')

            return order_list if not only_number else order_list_only_number

        except Exception as exc:
            print(f'\n❌ {__class__.CLASS_NAME} > get_order_list() ==> EXCEPTION: {exc}\n')
            return []


    def set_group_orders(self, division:int=30) -> str:
        """ Agrupo os pedidos em conjunto de 30 para importação em massa pelo sistema. """

        try:
            list_orders = self.get_order_list(True, True)
            print(f'\n🐞 SET_GROUP_ORDERS ==> LIST ORDERS: {list_orders}\n')
            total_orders = len(list_orders)
            division_factor = division
            set_division_quantity = math.ceil(total_orders/division_factor)

            index = 0
            division_list = list()

            for _ in range(set_division_quantity):

                set_divisions = list_orders[0+index:0+division_factor]
                division_list.append(f','.join([x for x in set_divisions]))

                index+=30
                division_factor+=30

            print(f'\n🐞 SET_GROUP_ORDERS ==> TOTAL PEDIDOS: {total_orders} // TOTAL DIVISÕES: {len(division_list)}\n')
            return '\n\n'.join(division_list)

        except Exception as exc:
            print(f'\n❌ {__class__.CLASS_NAME} > set_group_orders() ==> EXCEPTION: {exc}\n')
            return ''


    def generate_sheet(self):
        """ Gerar uma planilha com as informações do pedido extraída do sistema e do Asana. """

        try:
            sheet_title = f'FSYS_DAILYSHIPMENTS__SHEIN'.upper()
            sheet_hearder = ["Pedido", "Cliente", "Produto", "Data Coleta Shein", "Status Asana"]
            sheet_data = list()
            not_imported = list()

            set_orders = self.get_order_list()

            for order in set_orders:

                print(f'\n🐞 GENERATE_SHEET ==> ORDER NUMBER: {order[0]}\n')
                query_order = ORDER().filter_number(order[0])

                if query_order == None:
                    not_imported.append(order[0])

                    sheet_data.append(
                        (
                            order[0],
                            ' - ',
                            ' - ',
                            order[1],
                            ' PEDIDO NÃO IMPORTADO ',
                        )
                    )
                    continue

                query_product = PRODUCT().filter_number(order[0])
                set_products = ' NOT FOUND ' if query_product == None else "\n".join([f'{product.name} - QTD: {product.qty} UNID' for product in query_product])

                try:
                    ## OBTER STATUS ASANA
                    asana = AsanaAPI()
                    task_gid = query_order.order_task['gid'][0]
                    task_status = None
                    get_task = asana.get_a_task(task_gid)

                    if 'errors' in get_task:
                        print(f'\n❌ GENERATE_SHEET ==> TAREFA "{task_gid}" NÃO ENCONTRADA: {get_task}\n')

                    else:
                        for fild in get_task["data"]["custom_fields"]:
                            if fild["gid"] == "1202857995568623":
                                task_status = fild["enum_value"]
                                break

                except Exception as exc:
                    print(f'\n❌ {__class__.CLASS_NAME} > generate_sheet() ==> EXCEPTION ASANA TASK: {exc}\n')
                    task_status = {"name": ' EXCEPTION '}

                sheet_data.append(
                    (
                        query_order.order_number,
                        query_order.order_customer,
                        set_products,
                        order[1],
                        task_status["name"] if task_status != None else "",
                    )
                )

            excel = tablib.Dataset(*sheet_data, headers=sheet_hearder)
            excel.title = sheet_title

            with open(f'D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/{sheet_title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            print(f'\n🐞 GENERATE_SHEET ==> PLANILHA CRIADA COM SUCESSO! \n')
            print(f'\n🐞 GENERATE_SHEET ==> PEDIDOS NÃO IMPORTADOS NO SISTEMA: {f'\n'.join(not_imported)} \n')

        except Exception as exc:
            print(f'\n❌ {__class__.CLASS_NAME} > generate_sheet() ==> EXCEPTION: {exc}\n')
            return ''

import flet as ft
from view.component.snackbar import SnackBar_PATTERNS

## REPOSITORYS
from data.repository.company import CompanyRepository as COMPANY_REP
from data.repository.carrier import CarrierRepository as CARRIER
from data.repository.orderV2 import OrderRepositoryV2 as ORDER_REP
from data.repository.order_product import OrderProductRepository as PRODCT_REP
from data.repository.saleschannel import SalesChannelRepository as SALES_CHANNEL
from sqlalchemy import null

## CONTROLLERS
from controllers.date_control import date_create as DATE
from controllers.task_control import TaskControl as TASK

## SOURCE APIs
from source.api.shopeeApi import Shopee
from source.api.sheinApi import Shein



class Bulk_Orders:

    def __init__(self, page:ft.Page, user_system:dict) -> None:

        self.page = page
        self.user_system = user_system

        self.app_config = self.page.session.get("app_config")

        self.__imported_orders = list()
        self.__list_company_info = dict()

        ## WIDGETS:
        self.snackbar = SnackBar_PATTERNS(self.page)
        ## ---------        


    def create_view(self) -> ft.Column:
        """ Cria a visualização para o usuário. """

        try:
            self.__get_integration = ft.Dropdown(
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                content_padding=ft.padding.symmetric(vertical=1, horizontal=10),
                filled=True,
                width=180,
                height=35,
                options=[
                    ft.dropdown.Option(key="shein_api", text="Shein API"),
                    # ft.dropdown.Option(key="shein_excel", text="Shein API +EXCEL"),
                    ft.dropdown.Option(key="shopee_api", text="Shopee API"),
                ]
            )

            self.__get_company = ft.Dropdown(
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                content_padding=ft.padding.symmetric(vertical=1, horizontal=10),
                filled=True,
                width=150,
                height=35,
                options=self.__get_companys(),
            )

            self.__get_order_numbers = ft.TextField(
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                content_padding=ft.padding.symmetric(vertical=1, horizontal=10),
                width=250,
                height=35,
                on_submit=self.__start_bulk_import
            )

            self.__set_content_import = ft.Column(scroll=ft.ScrollMode.AUTO, auto_scroll=True)

            self.__set_content_progress = ft.Row()

            return ft.Column(
                controls=[
                    ft.ResponsiveRow(
                        controls=[

                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(name=ft.icons.LIST, size=12, color=ft.colors.ON_BACKGROUND),
                                            ft.Text(value="Integração", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                        ],
                                        spacing=3
                                    ),
                                    self.__get_integration
                                ],
                                spacing=5,
                                col=3
                            ),

                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(name=ft.icons.BUSINESS, size=12, color=ft.colors.ON_BACKGROUND),
                                            ft.Text(value="Empresa", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                        ],
                                        spacing=3
                                    ),
                                    self.__get_company
                                ],
                                spacing=5,
                                col=3
                            ),

                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(name=ft.icons.NUMBERS, size=12, color=ft.colors.ON_BACKGROUND),
                                            ft.Text(value="Número Pedidos", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                        ],
                                        spacing=3
                                    ),
                                    self.__get_order_numbers
                                ],
                                spacing=5,
                                col=6
                            ),

                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),

                    ft.Container(
                        content=self.__set_content_import,
                        bgcolor=ft.colors.with_opacity(0.3, ft.colors.BACKGROUND),
                        border_radius=ft.border_radius.all(7),
                        padding=ft.padding.symmetric(15,20),
                        margin=ft.margin.symmetric(15),
                        width=600,
                        height=350,
                    ),

                    ft.Divider(height=0.15, color=ft.colors.with_opacity(0.15, ft.colors.ON_BACKGROUND)),

                    ft.Container(
                        content=self.__set_content_progress,
                        border_radius=ft.border_radius.all(7),
                        padding=ft.padding.symmetric(15,20),
                        # margin=ft.margin.symmetric(15),
                        alignment=ft.alignment.center
                        # width=600,
                        # height=350,
                    )

                ],
                width=600,
                height=500,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > create_view() ==> EXCEPTION: {exc}\n')
            return None


    def __start_bulk_import(self, e):
        """ Inicia o processo de importação de pedidos em massa. """  

        try:
            get_orders = self.__get_orders()

            if get_orders == None:
                self.add_status(index_order=None, status="error", order_number="")
                return None

            self.__disabled_form()

            all_order = len(get_orders)
            index_order = 1
            index_sucess = 0
            index_fall = 0
            index_task = 0

            for order in get_orders:

                print(f'\n🐞 BULK_ORDERS > IMPORTANDO PEDIDO {index_order}/{all_order} DE {order["orderChannel"]}, POR {self.user_system["name"]} \n')

                self.add_progress(qty_progress=[index_order, all_order], qty_status=[index_sucess, index_fall, index_task])

                shipping_method = self.__get_carrier(order["shippingMethod"])
                sales_channel = self.__get_sales_channel(marketplace=order["orderChannel"], company=self.__get_company.value)

                system_comment = f'Order {order["orderChannel"]} #{order["orderNumber"]}, imported in bulk from {self.__get_integration.value.upper()} | {self.app_config["app"]["name"]} v{self.app_config["app"]["version"]} - {self.app_config["app"]["build"]}'

                save_in_db = self.__save_order_in_db(index_order=index_order, order=order, carrier=shipping_method, sys_comment=system_comment)

                if not save_in_db:
                    self.add_status(index_order=index_order, status="imported_failed", order_number=order["orderNumber"])
                    index_order += 1
                    index_fall += 1
                    continue

                else:
                    self.add_status(index_order=index_order, status="imported_successfully", order_number=order["orderNumber"])

                    index_sucess += 1
                    self.add_progress(qty_progress=[index_order, all_order], qty_status=[index_sucess, index_fall, index_task])

                    create_task = self.__create_task_in_asana(order=order, carrier=shipping_method, sales_channel=sales_channel, sys_comment=system_comment)

                    if create_task == None:
                        self.add_status(index_order=index_order, status="created_failed", order_number=order["orderNumber"])
                        index_order += 1
                        continue

                    else:
                        get_order_in_db = ORDER_REP().filter_number(order["orderNumber"])

                        ORDER_REP().update(
                            id=get_order_in_db.id,
                            fild="order_task",
                            data={"gid": [create_task["data"]["gid"]]}
                        )

                        self.add_status(index_order=index_order, status="created_successfully", order_number=order["orderNumber"])

                index_order += 1
                index_task += 1

            self.add_progress(end=True, qty_progress=[index_order-1, all_order], qty_status=[index_sucess, index_fall, index_task])
            self.__clear_form()

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __start_bulk_import() ==> EXCEPTION: {exc}\n')
            return None


    ## OBTEM INFORMAÇÕES DO SISTEMA -------

    def __get_companys(self) -> list | None:
        """ Obtem as empresas cadastradas no sistema e retorna uma lista com os nomes para selecionar. """

        try:
            get_companys = COMPANY_REP().filter_all()
            list_company_select = list()

            for company in get_companys:
                list_company_select.append(ft.dropdown.Option(key=company.name, text=f"Fadrix {str(company.name).split(" ")[0]}"))
                self.__list_company_info[company.name] = company.asanaID

            return list_company_select

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __get_companys() ==> EXCEPTION: {exc}\n')
            return None


    def __get_carrier(self, carrier_id:int) -> dict:
        """ Obtem a forma de envio cadastrada no sistema pelo ID informado, e retorna as informações da mesma. """

        try:
            get_carrier = CARRIER().filter_id(carrier_id)
            return {"id": get_carrier.asanaID, "name": get_carrier.name} if get_carrier != None else {"id": "1204067809318932", "name": "NULL"}

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __get_companys() ==> EXCEPTION: {exc}\n')
            return {"id": "1204067809318932", "name": "NULL"}


    def __get_sales_channel(self, marketplace:str, company:str) -> dict:
        """ Busca as informações do canal de envio para importação no sistema. """

        try:
            search_sales_channel = SALES_CHANNEL().filter_marketplace(marketplace)
            for channel in search_sales_channel:
                if channel.company["name"] == company:                    
                    return {"id": channel.asanaID, "name": channel.name}

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __get_sales_channel() ==> EXCEPTION: {exc}\n')
            return None

    ##  -------



    def __check_info(self) -> bool:
        """ Checa as informações para validar antes de importar. """

        try:

            if self.__get_integration.value == None or self.__get_company == None:
                self.snackbar.warning("Selecione uma integração e empresa para continuar.")
                return False

            if len(self.__get_order_numbers.value) == 0:
                self.snackbar.warning("Informe os números dos pedidos para continuar.")
                return False
            
            total_orders = len(self.__get_order_numbers.value.replace(" ", "").split(sep=','))

            if total_orders == 1:
                self.snackbar.warning("Informe no mínimo dois números de pedidos para continuar.")
                return False

            if self.__get_integration.value == "shopee_api" and total_orders > 50:
                self.snackbar.warning("Limite máximo de 50 pedidos para importação em massa da Shopee ultrapasado.")
                return False

            if self.__get_integration.value == "shein_api" and total_orders > 30:
                self.snackbar.warning("Limite máximo de 30 pedidos para importação em massa da Shein ultrapasado.")
                return False

            return True

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __check_info() ==> EXCEPTION: {exc}\n')
            return None


    def __get_orders(self) -> list:
        """ Busca os dados dos pedidos direto no marketplace. """

        try:
            self.__set_content_import.controls.clear()
            self.__set_content_import.update()
            self.page.update()

            check = self.__check_info()

            if not check:
                return None

            match self.__get_integration.value:

                case "shopee_api":
                    get_shopee = Shopee(self.__get_company.value).bulk_orders_pattern(order_numbers=self.__get_order_numbers.value)
                    if "Error" in get_shopee:
                        return None
                    else:
                        return get_shopee

                case "shein_api":
                    get_shein = Shein(self.__get_company.value).bulk_orders_pattern(order_numbers=str(self.__get_order_numbers.value).split(","))
                    if "Error" in get_shein:
                        return None
                    else:
                        return get_shein


        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __get_orders() ==> EXCEPTION: {exc}\n')
            return None


    ## SALVA OS PEDIDOS NO SISTEMA  -------

    def __save_order_in_db(self, index_order:int, order:dict, carrier:dict, sys_comment:str) -> bool:
        """ Salva o pedido no banco de dados do sistema. """

        try:
            set_order = order
            set_carrier = carrier
            set_sys_comment = sys_comment

            if ORDER_REP().filter_number(set_order["orderNumber"]) != None:
                self.add_status(index_order=index_order, status="order_already_imported", order_number=set_order["orderNumber"])
                return False

            db = ORDER_REP().insert(
                order_status="Importado",
                order_dateImport=DATE(),
                order_userSystem=self.user_system["name"],
                order_number=set_order["orderNumber"],
                order_reference=null(),
                order_channel=set_order["orderChannel"],
                order_company=set_order["orderCompany"],
                order_date=set_order["orderDate"],
                order_customer=set_order["customer"],
                order_customerID=set_order["customerID"],
                order_customerNickname=set_order["customerNickname"],
                order_customerPhone=set_order["customerPhone"],
                order_customerEmail=null(),
                order_shippingAddress=set_order["shippingAddress"],
                order_shippingMethod=set_carrier["name"],
                order_shippingDate=set_order["shippingDate"],
                order_shippingDateMKP=set_order["original_shippingDate"],
                order_shippingTracking=null(),
                order_task={"gid": []},
                order_historic=set_sys_comment
            )

            for product in set_order["Products"]:
                PRODCT_REP().insert(
                    order_number=set_order["orderNumber"],
                    name=product["produto"],
                    sku=product["sku"],
                    qty=product["qtd"],
                    icon=product["icon"],
                    customization=product["personalizacao"]
                )

            return True

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __save_order_in_db() ==> EXCEPTION: {exc}\n')
            return False


    def __create_task_in_asana(self, order:dict, carrier:dict, sales_channel:dict, sys_comment:str):
        """ Importar o pedido como tarefa no Asana. """

        try:
            set_order = order
            set_carrier = carrier
            set_sales_channel = sales_channel
            set_sys_comment = sys_comment

            tag_rj = False if set_order["shippingAddress"]["uf"] != "RJ" and set_order["shippingAddress"]["uf"] != "Rio de Janeiro" else True

            data_task = {
                "completion_date": set_order["shippingDate"],
                "project": "arte_final",
                "custom_fields": {
                    "channel": set_sales_channel["id"],
                    "company": self.__list_company_info[set_order["orderCompany"]],
                    "attendant": self.user_system["id"],
                    "shippingMethod": set_carrier["id"]
                },
                "info": {
                    "number": set_order["orderNumber"],
                    "customer": set_order["customer"],
                    "date": set_order["orderDate"].strftime('%d/%m/%Y %H:%M:%S'),
                    "channel": set_sales_channel["name"],
                    "company": set_order["orderCompany"],
                    "attendant": self.user_system["name"],
                    "address": set_order["shippingAddress"]["enderecoCompleto"],
                    "shippingMethod": set_carrier["name"],
                    "products": set_order["Products"]
                },
                "comments": [{"text": set_sys_comment, "pinned" : False}],
                # "tags": {
                #     "#RJ":tag_rj
                # }
            }

            create_task = TASK().create(type_body="order", task_data=data_task)
            return create_task

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __create_task_in_asana() ==> EXCEPTION: {exc}\n')
            return None

    ##  -------


    def add_status(self, index_order:int, status:str, order_number:str):
        """ Adiciona informação de status da importação em tela para alertar o usuário. """

        try:
            match status:

                case "imported_successfully":
                    text_status = ft.Text(value=f'{index_order} _ ✅ PEDIDO {order_number} → SUCESSO NA IMPORTAÇÃO PARA O SISTEMA.', color=ft.colors.ON_BACKGROUND, size=12, col=10)

                case "imported_failed":
                    text_status = ft.Text(value=f'{index_order} _ ❌ PEDIDO {order_number} → FALHA NA IMPORTAÇÃO PARA O SISTEMA.', color=ft.colors.ON_BACKGROUND, size=12, col=10)

                case "created_successfully":
                    text_status = ft.Text(value=f'{index_order} _ ✏️ PEDIDO {order_number} → SUCESSO AO CRIAR A TAREFA NO ASANA.', color=ft.colors.ON_BACKGROUND, size=12, col=10)

                case "created_failed":
                    text_status = ft.Text(value=f'{index_order} _ ❌ PEDIDO {order_number} → FALHA AO CRIAR A TAREFA NO ASANA.', color=ft.colors.ON_BACKGROUND, size=12, col=10)

                case "order_already_imported":
                    text_status = ft.Text(value=f'{index_order} _ ⚠️ PEDIDO {order_number} → PEDIDO JÁ ESTÁ IMPORTADO NO SISTEMA.', color=ft.colors.ON_BACKGROUND, size=12, col=10)

                case "error":
                    text_status = ft.Text(value=f'⚠️ ERRO - NÃO FOI POSSÍVEL BUSCAR OS PEDIDOS DA INTEGRAÇÃO {str(self.__get_integration.value).upper()} | {self.__get_company.value}, VERIFIQUE A CONTA SELECIONADA OU ENTRE EM CONTATO COM O SUPORTE.', color=ft.colors.ON_BACKGROUND, size=12, col=10)

            info_status = ft.ResponsiveRow(
                controls=[
                    text_status,
                    ft.IconButton(icon=ft.icons.COPY, icon_color=ft.colors.ON_BACKGROUND, icon_size=14, data=order_number, on_click=self.__clipboard, col=2)
                ],
                vertical_alignment = ft.CrossAxisAlignment.CENTER
            )

            self.__set_content_import.controls.append(info_status)
            self.__set_content_import.update()
            self.page.update()

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > add_status() ==> EXCEPTION: {exc}\n')
            return None


    def add_progress(self, end:bool=False, qty_progress:list=[0,0], qty_status:list=[0,0,0]):
        """ Adiciona informações de progresso para o cliente acompanhar o andamento. """

        try:

            self.__set_content_progress.controls.clear()

            progress_bar = ft.ProgressRing(width=16, height=16, color=ft.colors.PRIMARY) if end == False else ft.Icon(name=ft.icons.CHECK_BOX_SHARP)
            text_status = "PROCESSANDO" if end == False else "PROCESSADO"

            info_progress = ft.Row(
                controls=[

                    ft.Container(
                        content=ft.Row(
                            controls=[
                                progress_bar,
                                ft.Text(value=f'{text_status} {qty_progress[0]}/{qty_progress[1]}', size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_BACKGROUND)
                            ]
                        ),
                        margin=ft.margin.only(right=20),
                        col=6
                    ),

                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(value='✅ SUCESSO', size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                ft.Text(value=f'{qty_status[0]}', size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_BACKGROUND)
                            ]
                        ),
                        bgcolor=ft.colors.with_opacity(0.15, ft.colors.PRIMARY),
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.symmetric(10,10),
                        col=2
                    ),

                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(value='❌ FALHA', size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                ft.Text(value=f'{qty_status[1]}', size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_BACKGROUND)
                            ]
                        ),
                        bgcolor=ft.colors.with_opacity(0.15, ft.colors.PRIMARY),
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.symmetric(10,10),
                        col=2
                    ),

                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(value='✏️ ASANA', size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                ft.Text(value=f'{qty_status[2]}', size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_BACKGROUND)
                            ]
                        ),
                        bgcolor=ft.colors.with_opacity(0.15, ft.colors.PRIMARY),
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.symmetric(10,10),
                        col=2
                    ),

                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )

            self.__set_content_progress.controls.append(info_progress)
            self.__set_content_progress.update()
            self.page.update()

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > add_progress() ==> EXCEPTION: {exc}\n')
            return None


    def __clipboard(self, e):
        """ Função para copiar dados para a área de transferência """

        try:
            self.page.set_clipboard(e.control.data)
            self.snackbar.clipboard()
            self.page.update()

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __clipboard() ==> EXCEPTION: {exc}\n')
            return None


    def __clear_form(self):
        """ Limpa o formulário de pesquisa de pedidos. """

        try:
            for fild in [self.__get_integration, self.__get_company, self.__get_order_numbers]:
                fild.value = None
                fild.disabled = False
                fild.update()
                self.page.update()

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __clear_form() ==> EXCEPTION: {exc}\n')
            return None
        

    def __disabled_form(self):
        """ Bloqueia o formulário para evitar ações em processamento. """

        try:
            for fild in [self.__get_integration, self.__get_company, self.__get_order_numbers]:
                fild.disabled = True
                fild.update()
                self.page.update()

        except Exception as exc:
            print(f'\n❌ BULK_ORDERS > __disabled_form() ==> EXCEPTION: {exc}\n')
            return None        

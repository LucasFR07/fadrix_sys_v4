import flet as ft
from flet import (
    Page, UserControl, DataTable, DataColumn, DataRow, DataCell, Container, Column, Row, Ref, Text, TextStyle, TextField, Divider, MainAxisAlignment, Icon, Image, ScrollMode, icons, margin, padding, alignment, border_radius, Tabs, Tab, PopupMenuButton, PopupMenuItem )


import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
import tablib

## CONEXÃƒO COM DADOS
from data.repository.orderV2 import OrderRepositoryV2 as ORDER
from data.repository.order_product import OrderProductRepository as PRODUCT
from data.repository.saleschannel import SalesChannelRepository as CHANNEL
from data.repository.status import StatusRepository as STATUS

## CONTROLES DO SISTEMA
from controllers.date_control import date_create as DATE
from controllers.date_control import *
from controllers.notice_control import NoticeControl

## COMPONENTES TEMPLATE
from view.component.buttons import ButtonsComponents as BUTTON
from view.component.dialog import Dialog
from view.component.snackbar import SnackBar_PATTERNS

## MODULES TEMPLATE
from view.modules.order.dashboard import OrderDashboard
from view.modules.order.reputation import ReputationDashboard
from view.modules.order.data_analysis import OrderAnalysis as ANLY
from view.modules.in_bulk.bulk_orders import Bulk_Orders

## WIDGET TEMPLATE
from view.widget.pagination import Pagination

## API
from source.api.asanaApi import AsanaAPI
from source.api.sheinApi import Shein
from source.api.shopeeApi import Shopee
from source.api.meliApi import MercadoLivre
from source.api.magis5 import Magis5


class OrderList(UserControl):

    def __init__(self, page:Page):
        super().__init__()
        self.page = page

        # INFORMAÃ‡Ã•ES DE SESSÃƒO:
        self.user_system = self.page.client_storage.get("user_info")
        self.app_config = self.page.session.get("app_config")
        ## ---------

        ## WIDGETS:
        self.snackbar = SnackBar_PATTERNS(self.page)
        self.alert = Dialog(self.page)
        ## ---------

        self.group_true1 = ['Administrador', 'Vendas', 'Gerente']
        self.group_true2 = ['Administrador', 'Gerente']

        ## VARIÃVEIS (REFs):
        self.pagination = None
        self.search_order = Ref[TextField]()
        self.btn_clear = Ref[Container]()
        self.tabs_container = Ref[Container]()
        self.tabs_order = Ref[Tabs]()
        self.total_shipping = Ref[Text]()
        self.text_channel = Ref[Text]()
        self.text_days = Ref[Text]()
        ## ---------

        self.filter_channel = None
        self.filter_days = None
        self.filter_yesterday = False

        self.page.on_resize = self.on_resize
        self.table_width = self.page.width if self.page.platform != "android" else self.page.width*2

        self.order_table = DataTable(
            sort_column_index=0,
            sort_ascending=True,
            heading_row_color= ft.colors.SURFACE_VARIANT,
            heading_row_height=45,
            data_row_color={"hovered": ft.colors.INVERSE_PRIMARY},
            data_row_max_height=float("inf"),
            divider_thickness=0,
            column_spacing=50,
            columns=[
                DataColumn(
                    Text("Canal de Venda", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Canal de Venda",
                ),
                DataColumn(
                    Text("Conta", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Conta Empresa",
                ),
                DataColumn(
                    Text("NÂº Pedido", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="NÃºmero do Pedido"
                ),
                DataColumn(
                    Text("Cliente", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Nome do Cliente",
                ),
                DataColumn(
                    Text("Forma de Envio", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Forma de Envio",
                ),
                DataColumn(
                    Text("Data de Envio", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Data de Envio",
                ),
            ],
            width=self.table_width
        )

        self.shipping_table = DataTable(
            sort_column_index=0,
            sort_ascending=True,
            heading_row_color= ft.colors.SURFACE_VARIANT,
            heading_row_height=45,
            data_row_color={"hovered": ft.colors.INVERSE_PRIMARY},
            data_row_max_height=float("inf"),
            divider_thickness=0,
            column_spacing=50,
            columns=[
                DataColumn(
                    Text("Canal de Venda", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Canal de Venda",
                ),
                DataColumn(
                    Text("Conta", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Conta Empresa",
                ),
                DataColumn(
                    Text("Pedido", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Pedido"
                ),
                DataColumn(
                    Text("Data de Envio (ATD)", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Data de Envio",
                ),
                DataColumn(
                    Text("Data de Envio (MKP)", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Data de Envio (MKP)",
                ),
                DataColumn(Text("", color=ft.colors.ON_BACKGROUND, weight="w700", size=14)),                
            ],
            width=self.table_width
        )

        self.tabs_module_order = Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    tab_content=Row(
                        controls=[
                            Icon(name=icons.LIST_ROUNDED, color=ft.colors.ON_BACKGROUND, size=16),
                            Text(value="Pedidos", color=ft.colors.ON_BACKGROUND, size=14)
                        ],
                    )
                ),
                Tab(
                    tab_content=Row(
                        controls=[
                            Icon(name=icons.LOCAL_SHIPPING_OUTLINED, color=ft.colors.ON_BACKGROUND, size=16),
                            Text(value="Envios", color=ft.colors.ON_BACKGROUND, size=14)
                        ],
                    )
                ),
                Tab(
                    tab_content=Row(
                        controls=[
                            Icon(name=icons.TIMELINE_OUTLINED, color=ft.colors.ON_BACKGROUND, size=16),
                            Text(value="Analytics", color=ft.colors.ON_BACKGROUND, size=14)
                        ],
                        visible=True if self.user_system['usr_group'] in self.group_true2 else False
                    )
                ),
                Tab(
                    tab_content=Row(
                        controls=[
                            Icon(name=icons.STARS, color=ft.colors.ON_BACKGROUND, size=16),
                            Text(value="ReputaÃ§Ã£o", color=ft.colors.ON_BACKGROUND, size=14)
                        ],
                        visible=True if self.user_system['usr_group'] in self.group_true2 else False
                    )
                ),
            ],
            indicator_color=ft.colors.PRIMARY,
            divider_color=ft.colors.BACKGROUND,
            height=37,
            # width=600,
            on_change=self.change_tabs
        )

        self.list_orders(filter=self.filter_channel, period=self.filter_days)


    def on_resize(self, e):

        """ Atualiza a largura das tabelas de pedidos. """

        self.table_width = self.page.width if self.page.platform != "android" else self.page.width*2

        try:

            match self.tabs_module_order.selected_index:

                case 0:
                    self.order_table.width = self.table_width
                    self.order_table.update()
                case 2:
                    self.shipping_table.width = self.table_width
                    self.shipping_table.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > on_resize() ==> EXCEPTION: {exc}\n')

        finally:
            self.page.update()


    def build(self):

        view = Container(
            content=Column(
                controls=[
                    Container( #HEADER CONTAINER
                        content=Column(
                            controls=[
                                Container(
                                    content=Row(
                                        controls=[
                                            Column(
                                                controls=[
                                                    Row(
                                                        controls=[
                                                            Container(
                                                                content=Icon(name=icons.SHOPPING_CART, size=25, color=ft.colors.ON_BACKGROUND),
                                                                width=40,
                                                                height=40,
                                                                bgcolor=ft.colors.INVERSE_PRIMARY,
                                                                border_radius=border_radius.all(10)
                                                            ),
                                                            Text(value="Gerenciamento de Vendas", size=25, weight="w700", color=ft.colors.ON_BACKGROUND)
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            Column(
                                                controls=[
                                                    Row(
                                                        controls=[
                                                            BUTTON(page=self.page, icon="add", text="adicionar", style="small", color="primary", event=self.import_order) if self.user_system['usr_group'] in self.group_true1 else Text(),
                                                            ft.PopupMenuButton(
                                                                items=[
                                                                    ft.PopupMenuItem(text="Importar Em Massa (beta)", on_click=self.open_bulk_orders, icon=ft.icons.IMPORT_CONTACTS_SHARP),
                                                                ]
                                                            )
                                                        ],
                                                        spacing=10
                                                    ),
                                                ]
                                            )
                                        ],
                                        alignment="spaceBetween"
                                    ),
                                    margin=margin.symmetric(vertical=25, horizontal=25)
                                ),
                                Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.15),
                                Container(
                                    content=Row(
                                        controls=[
                                            Container(
                                                content = self.tabs_module_order,
                                                padding = padding.all(0),
                                                margin = margin.all(0),
                                            ),
                                            Container(
                                                content= Row(
                                                    controls=[
                                                        Column(
                                                            controls=[
                                                                Row(
                                                                    controls=[
                                                                        TextField(
                                                                            icon=icons.SEARCH_OUTLINED, 
                                                                            hint_text="Buscar",
                                                                            hint_style=TextStyle(italic=True, size=14),
                                                                            text_style=TextStyle(size=14, weight="w600"),
                                                                            color=ft.colors.ON_BACKGROUND,
                                                                            bgcolor=ft.colors.SURFACE_VARIANT,
                                                                            border_color=ft.colors.with_opacity(0.1, ft.colors.OUTLINE),
                                                                            border_radius=15,
                                                                            focused_color=ft.colors.PRIMARY,
                                                                            focused_border_color=ft.colors.PRIMARY,
                                                                            content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                            width=250,
                                                                            height=35,
                                                                            ref=self.search_order,
                                                                            on_submit=self.__tab_order
                                                                        ),
                                                                        Container(
                                                                            content=BUTTON(page=self.page, text="limpar", style="small", color="info", event=self.clear_search).outline(),
                                                                            visible=False,
                                                                            ref=self.btn_clear
                                                                        ),
                                                                    ]
                                                                )
                                                            ]
                                                        ),
                                                        Column(
                                                            controls=[
                                                                PopupMenuButton(
                                                                    content=Container(
                                                                        content=Row([Icon(icons.FILTER_LIST, color=ft.colors.PRIMARY), Text(value=None, color=ft.colors.PRIMARY, ref=self.text_channel)]),
                                                                        border_radius=border_radius.all(50),
                                                                        padding=padding.symmetric(6,10),
                                                                        on_hover=self.hover_filters
                                                                    ),
                                                                    # icon=icons.FILTER_LIST,
                                                                    tooltip="Filtrar por Canal de Venda", 
                                                                    items=[
                                                                        PopupMenuItem(icon=icons.STOREFRONT, text="Amazon", on_click=self.drop_filter),
                                                                        PopupMenuItem(icon=icons.STOREFRONT, text="Americanas", on_click=self.drop_filter),
                                                                        PopupMenuItem(icon=icons.STOREFRONT, text="Magazine Luiza", on_click=self.drop_filter),
                                                                        PopupMenuItem(icon=icons.STOREFRONT, text="Mercado Livre", on_click=self.drop_filter),
                                                                        PopupMenuItem(icon=icons.STOREFRONT, text="Shein", on_click=self.drop_filter),
                                                                        PopupMenuItem(icon=icons.STOREFRONT, text="Shopee", on_click=self.drop_filter),
                                                                        PopupMenuItem(icon=icons.STOREFRONT, text="Prestashop", on_click=self.drop_filter),
                                                                        PopupMenuItem(),
                                                                        PopupMenuItem(icon=icons.CLEAR_ALL, text="Limpar Filtro", on_click=self.drop_filter),
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                        Column(
                                                            controls=[
                                                                PopupMenuButton(
                                                                    content=Container(
                                                                        content=Row([Icon(icons.CALENDAR_MONTH, color=ft.colors.PRIMARY), Text(value=None, color=ft.colors.PRIMARY, ref=self.text_days)]),
                                                                        border_radius=border_radius.all(50),
                                                                        padding=padding.symmetric(6,10),
                                                                        on_hover=self.hover_filters
                                                                    ),
                                                                    # icon=icons.CALENDAR_MONTH,
                                                                    tooltip="Filtrar por PerÃ­odo",
                                                                    items=[
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="Ontem", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="AmanhÃ£", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="7 dias", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="15 dias", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="30 dias", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="60 dias", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="90 dias", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(icon=icons.CALENDAR_TODAY, text="180 dias", on_click=self.drop_filterDays),
                                                                        PopupMenuItem(),
                                                                        PopupMenuItem(icon=icons.CLEAR_ALL, text="Limpar Filtro", on_click=self.drop_filterDays)
                                                                    ],
                                                                ),
                                                            ]
                                                        ),                                                    
                                                    ]
                                                ),
                                                padding=padding.all(0),
                                                margin=margin.symmetric(horizontal=15),
                                            ),
                                        ],
                                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                                        spacing=25,
                                        scroll=ft.ScrollMode.HIDDEN,
                                    ),
                                    margin=margin.symmetric(vertical=10, horizontal=25),
                                    alignment=alignment.center
                                )
                            ],
                            spacing=0
                        ),
                        bgcolor=ft.colors.BACKGROUND,
                    ),
                    Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.15),

                    Container(
                        ref=self.tabs_container,
                        content=self.__tab_list(),
                        expand=True
                    ),
                ],
                spacing=0
            ),
        )
        return view


    def open_bulk_orders(self, e):
        """ Abre o processo de importaÃ§Ã£o em massa de pedidos. """

        try:
            bulk = Bulk_Orders(page=self.page, user_system={"id": self.user_system["asanaID"], "name": self.user_system["name"]}).create_view()

            self.alert.default_dialog(
                contt = bulk,
                act = None,
                title = Text(value="âš™ï¸ ImportaÃ§Ã£o Em Massa", color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_500)
            )

            self.page.dialog = self.alert
            self.alert.open = True
            self.page.update()

        except Exception as exc:
            print(exc)


    ## TABS ---------

    def __tab_list(self):

        self.tabs_module_order.selected_index=0
        self.order_table.width = self.table_width

        return Column(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=Row(controls=[self.order_table], scroll=ScrollMode.HIDDEN),
                                margin=margin.symmetric(vertical=10, horizontal=15),
                            ),
                        ],
                        scroll=ScrollMode.ALWAYS
                    ),
                    expand=True,
                    padding=padding.symmetric(horizontal=10)
                ),

                Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.2),
                Container(
                    content=Row(
                        controls=[self.pagination],
                        alignment=MainAxisAlignment.CENTER
                    ),
                    height=43,
                    alignment=alignment.center,
                    padding=padding.symmetric(vertical=10),
                    margin=margin.symmetric(vertical=15)
                )
            ]
        )


    def __tab_order(self, e):

        self.tabs_module_order.selected_index=0
        self.order_table.width = self.table_width


        if self.tabs_container.current.content != None:
            self.tabs_container.current.content.clean()
            self.tabs_container.current.update()

        if not e.control.value:
            self.tabs_container.current.content = self.__tab_list()
            self.tabs_container.current.update()
            self.list_orders(filter=self.filter_channel, period=self.filter_days)

        self.list_order(e.control.value)

        self.tabs_container.current.content = Column(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=Row(controls=[self.order_table], scroll=ScrollMode.HIDDEN),
                                margin=margin.symmetric(vertical=10, horizontal=15)
                            )
                        ],
                        scroll=ScrollMode.ALWAYS
                    ),
                    expand=True,
                    padding=padding.symmetric(horizontal=10)
                ),
            ]
        )

        self.tabs_container.current.update()


    def __tab_waiting(self):

        self.tabs_module_order.selected_index=1        
        self.tabs_module_order.update()
        self.page.update()

        self.set_column_waiting = Column(
            alignment=MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.ALWAYS
        )

        self.set_column_waitingTask = Column(
            alignment=MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.ALWAYS
        )

        self.set_column_waitingDuplicate = Column(
            alignment=MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.ALWAYS
        )

        self.list_waiting(channel=self.filter_channel)

        return ft.ResponsiveRow(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=Text(value="âŒ› Pedidos Aguardando", size=15, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                border_radius=5,
                                alignment=alignment.center,
                                padding=padding.symmetric(7,10)
                            ),
                            self.set_column_waiting
                        ],
                    ),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.OUTLINE_VARIANT),
                    border_radius=10,
                    alignment=alignment.top_center,
                    padding=padding.symmetric(5,5),
                    margin=margin.symmetric(15,10),
                    # col=4 if self.page.platform != "android" else None
                ),

                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=Text(value="â›” Pedidos Sem Tarefa (Asana)", size=15, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                border_radius=5,
                                alignment=alignment.center,
                                padding=padding.symmetric(7,10)
                            ),
                            self.set_column_waitingTask
                        ],
                    ),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.OUTLINE_VARIANT),
                    border_radius=10,
                    alignment=alignment.top_center,
                    padding=padding.symmetric(5,5),
                    margin=margin.symmetric(15,10),
                    # col=4 if self.page.platform != "android" else None
                ),

                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=Text(value="â›” Pedidos Duplicados", size=15, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                border_radius=5,
                                alignment=alignment.center,
                                padding=padding.symmetric(7,10)
                            ),
                            self.set_column_waitingDuplicate
                        ],
                    ),
                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.OUTLINE_VARIANT),
                    border_radius=10,
                    alignment=alignment.top_center,
                    padding=padding.symmetric(5,5),
                    margin=margin.symmetric(15,10),
                    # col=4 if self.page.platform != "android" else None
                ),

            ],
            scroll=ScrollMode.HIDDEN
        )


    def __tab_listShipping(self, day_filter:int=0):

        self.tabs_module_order.selected_index=1
        self.tabs_module_order.update()
        self.shipping_table.width = self.table_width
        self.page.update()

        # self.list_shipping(channel=self.filter_channel, day=day_filter)


        self.reports_shipping = ft.Dropdown(
            value='LP',
            border_radius=ft.border_radius.all(5),
            filled=True,
            options=[
                ft.dropdown.Option(key='LP', text="Listagem PadrÃ£o"),
                # ft.dropdown.Option(key='LPA', text="Listagem PadrÃ£o + Asana"),
                ft.dropdown.Option(key='LSTA', text="Listagem Shopee FULL"),
                ft.dropdown.Option(key='LSED', text="Listagem Shopee ENTREGA DIRETA"),
                # ft.dropdown.Option(key='LSPA', text="Listagem Shopee STT. PROCESSADOS + Asana"),
                ft.dropdown.Option(key='LSF', text="Listagem Shein FULL"),
            ]
        )


        def match_action(e):
            
            match self.reports_shipping.value:

                case 'LP':
                    return self.report_dailyshipments()
                # case 'LPA':
                #     return self.report_dailyshipments_with_asana()
                case 'LSTA':
                    return self.report_dailyshipments_with_asana_shopee2()
                case 'LSED':
                    return self.report_dailyshipments_with_asana_shopeeFLEX()
                # case 'LSAA':
                #     return self.report_dailyshipments_with_asana_shopee3()
                # case 'LSPA':
                #     return self.report_dailyshipments_with_asana_shopee1()
                case 'LSF':
                    return self.report_dailyshipments_with_asana_shein()


        return Column(
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        Container(
                            content=ft.Column(controls=self.dispatch_schedule(), spacing=10),
                            padding=padding.symmetric(horizontal=10),
                            margin=ft.margin.symmetric(vertical=15),
                            col=5
                        ),
                        Container(
                            content=ft.Column(
                                controls=[
                                    ft.Container(
                                        content=ft.Text("RelatÃ³rios de Envio Marketplaces", size=18, weight=ft.FontWeight.W_600),
                                        padding=ft.padding.symmetric(10, 25)
                                    ),

                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                self.reports_shipping,
                                                ft.FilledButton(
                                                    text="Gerar RelatÃ³rio",
                                                    on_click=match_action
                                                )
                                            ],
                                            spacing=10
                                        ),
                                        bgcolor=ft.colors.BACKGROUND,
                                        border_radius=ft.border_radius.all(10),
                                        padding=ft.padding.symmetric(30, 25),
                                        alignment=ft.alignment.top_left
                                    )

                                ]

                            ),
                            padding=padding.symmetric(horizontal=10),
                            margin=ft.margin.symmetric(vertical=15),
                            col=7,
                            expand=True
                        )

                    ]
                ),

                #Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.2),

                # Container(
                #     content=Row(
                #         controls=[
                #             Row(
                #                 controls=[
                #                     Text(f'TOTAL {self.filter_channel if self.filter_channel != None else "GERAL"}:'.upper(), color=ft.colors.ON_BACKGROUND, weight="w700", size=16),
                #                     Text(f'{ANLY(0).total_shippingDay(channel=self.filter_channel, last_day=False)} Pedidos', color=ft.colors.ON_BACKGROUND, weight="w400", size=20, ref=self.total_shipping),
                #                 ],
                #                 vertical_alignment=ft.CrossAxisAlignment.CENTER
                #             ),
                #             PopupMenuButton(
                #                 content=Container(
                #                     content=Row([Icon(icons.DOWNLOAD, color=ft.colors.PRIMARY), Text(value="Download", weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY)]),
                #                     bgcolor=ft.colors.BACKGROUND,
                #                     border_radius=border_radius.all(50),
                #                     padding=padding.symmetric(10,17),
                #                     shadow=ft.BoxShadow(
                #                         spread_radius=-0.5,
                #                         blur_radius=0.1,
                #                         color=ft.colors.OUTLINE,
                #                         offset=ft.Offset(0, 1.2),
                #                         blur_style=ft.ShadowBlurStyle.NORMAL,
                #                     ),
                #                 ),
                #                 tooltip="Baixar planilha de envios em excel", 
                #                 items=[
                #                     PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem PadrÃ£o", on_click=self.report_dailyshipments),
                #                     PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem PadrÃ£o + Asana", on_click=self.report_dailyshipments_with_asana),
                #                     PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shopee STT. TODOS + Asana", on_click=self.report_dailyshipments_with_asana_shopee2),
                #                     PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shopee STT. EM ABERTO + Asana", on_click=self.report_dailyshipments_with_asana_shopee3),
                #                     PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shopee STT. PROCESSADOS + Asana", on_click=self.report_dailyshipments_with_asana_shopee1),
                #                     PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shein FULL", on_click=self.report_dailyshipments_with_asana_shein),
                #                 ],
                #             ),
                #         ],
                #         alignment=MainAxisAlignment.SPACE_BETWEEN,
                #         # spacing=10
                #     ),
                #     height=40,
                #     alignment=alignment.center,
                #     padding=padding.symmetric(vertical=0, horizontal=30),
                #     margin=margin.symmetric(vertical=15)
                # )                

            ]
        )


        return Column(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=Row(controls=[self.shipping_table], scroll=ScrollMode.HIDDEN),
                                margin=margin.symmetric(vertical=10, horizontal=15)
                            )
                        ],
                        scroll=ScrollMode.ALWAYS
                    ),
                    expand=True,
                    padding=padding.symmetric(horizontal=10)
                ),
                Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.2),
                Container(
                    content=Row(
                        controls=[
                            Row(
                                controls=[
                                    Text(f'TOTAL {self.filter_channel if self.filter_channel != None else "GERAL"}:'.upper(), color=ft.colors.ON_BACKGROUND, weight="w700", size=16),
                                    Text(f'{ANLY(0).total_shippingDay(channel=self.filter_channel, last_day=False)} Pedidos', color=ft.colors.ON_BACKGROUND, weight="w400", size=20, ref=self.total_shipping),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            PopupMenuButton(
                                content=Container(
                                    content=Row([Icon(icons.DOWNLOAD, color=ft.colors.PRIMARY), Text(value="Download", weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY)]),
                                    bgcolor=ft.colors.BACKGROUND,
                                    border_radius=border_radius.all(50),
                                    padding=padding.symmetric(10,17),
                                    shadow=ft.BoxShadow(
                                        spread_radius=-0.5,
                                        blur_radius=0.1,
                                        color=ft.colors.OUTLINE,
                                        offset=ft.Offset(0, 1.2),
                                        blur_style=ft.ShadowBlurStyle.NORMAL,
                                    ),
                                ),
                                tooltip="Baixar planilha de envios em excel", 
                                items=[
                                    PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem PadrÃ£o", on_click=self.report_dailyshipments),
                                    PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem PadrÃ£o + Asana", on_click=self.report_dailyshipments_with_asana),
                                    PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shopee STT. TODOS + Asana", on_click=self.report_dailyshipments_with_asana_shopee2),
                                    PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shopee STT. EM ABERTO + Asana", on_click=self.report_dailyshipments_with_asana_shopee3),
                                    PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shopee STT. PROCESSADOS + Asana", on_click=self.report_dailyshipments_with_asana_shopee1),
                                    PopupMenuItem(icon=icons.SIM_CARD_DOWNLOAD_OUTLINED, text="Listagem Shein FULL", on_click=self.report_dailyshipments_with_asana_shein),
                                ],
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        # spacing=10
                    ),
                    height=40,
                    alignment=alignment.center,
                    padding=padding.symmetric(vertical=0, horizontal=30),
                    margin=margin.symmetric(vertical=15)
                )                
            ]
        )


    def __tab_dashboard(self):

        self.tabs_module_order.selected_index=2
        self.tabs_module_order.update()
        self.page.update()

        return OrderDashboard(self.page, self.filter_days, self.filter_channel)


    def __tab_reputation(self):

        self.tabs_module_order.selected_index=3
        self.tabs_module_order.update()
        self.page.update()

        return ReputationDashboard(self.page)    


    def change_tabs(self, e):

        if self.tabs_container.current.content != None:
            self.tabs_container.current.content.clean()
            self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
            self.tabs_container.current.update()

        match e.control.selected_index:

            case 0:
                self.pagination = Pagination(self.page)
                self.list_orders(filter=self.filter_channel, period=self.filter_days)
                self.tabs_container.current.content = self.__tab_list()
                self.tabs_container.current.update()

            case 1:
                self.tabs_container.current.content = self.__tab_listShipping()
                self.tabs_container.current.update()

            case 2:
                if self.user_system['usr_group'] in self.group_true2:
                    self.tabs_container.current.content = self.__tab_dashboard()
                    self.tabs_container.current.update()

            case 3:
                if self.user_system['usr_group'] in self.group_true2:
                    self.tabs_container.current.content = self.__tab_reputation()
                    self.tabs_container.current.update()


    ## ---------



    def list_orders(self, currentPage=1, filter:str=None, period:int=None):

        """ Lista todos os pedidos dentro de um perÃ­odo de terminado, e de acordo com o filtro escolhido. """

        try:
            self.order_table.rows.clear()
            self.period = period if period != None else 60
            self.current_page = currentPage
            self.limite_query = 25 * self.current_page

            if filter != None:
                total_query = int(ANLY(self.period).total_sales(channel=filter, fild_date=True))
                if total_query == 0:
                    self.snackbar.not_found("NÃ£o encontrado pedidos no canal de venda {}.".format(filter))
                    self.page.update()                    
                self.max_pages = math.ceil(total_query/self.limite_query)
                offset_query = 25 * (self.current_page - 1)
                index = self.max_pages if self.max_pages <= 4 else 4
                if self.current_page == 1:
                    self.response_orders = ANLY(self.period).query_sales(channel=filter, limit=self.limite_query)
                else:
                    self.response_orders = ANLY(self.period).query_sales(channel=filter, limit=self.limite_query, offset=offset_query)

            else:
                total_query = int(ANLY(self.period).total_sales(fild_date=True))
                if total_query == 0:
                    self.snackbar.not_found("Ainda nÃ£o hÃ¡ pedidos importados!")
                    self.page.update()
                self.max_pages = math.ceil(total_query/self.limite_query)
                offset_query = 25 * (self.current_page - 1)
                index = self.max_pages if self.max_pages <= 4 else 4

                if self.current_page == 1:
                    self.response_orders = ANLY(self.period).query_sales(limit=self.limite_query)
                else:
                    self.response_orders = ANLY(self.period).query_sales(limit=self.limite_query, offset=offset_query)

            if self.response_orders is not None and not self.response_orders.empty:
                for order in self.response_orders.iterrows():
                    self.order_table.rows.append(
                        DataRow(
                            cells=[
                                DataCell(content=self.get_channel(order[1]['order_channel'])),
                                DataCell(Text(order[1]['order_company'], color=ft.colors.ON_BACKGROUND)),                        
                                DataCell(Text(f"{order[1]['order_number']}" if order[1]['order_reference'] == None else f"{order[1]['order_reference']}", color=ft.colors.ON_BACKGROUND)),
                                DataCell(Text(order[1]['order_customer'], color=ft.colors.ON_BACKGROUND)),
                                DataCell(Text(order[1]['order_shippingMethod'], color=ft.colors.ON_BACKGROUND)),
                                DataCell(Text(order[1]['order_shippingDate'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S'), color=ft.colors.ON_BACKGROUND)),
                            ],
                            selected=False,
                            data=order[1]['id'],
                            on_select_changed=self.view_order
                        )
                    )

            self.load_pagination(self.max_pages, self.current_page, index)
            self.update()
            self.page.update()
            
        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > list_orders() ==> EXCEPTION: {exc}\n')
            import traceback
            traceback.print_exc()
            self.snackbar.internal_error()
            self.page.update()


    def list_order(self, search:str):

        """ Lista apenas um pedido de acordo com a pesquisa. """

        self.order_table.rows.clear()
        self.btn_clear.current.visible = True
        self.pagination.visible = False
        self.update()
        self.page.update()

        order = ORDER()
        list_query = [order.filter_number(search), order.filter_reference(search), order.filter_customer(search)]

        validate_none = False
        validate_data = False

        for query_order in list_query:

            if query_order == None:
                validate_none = True

            else:
                if type(query_order) == list:

                    if len(query_order) != 0:
                        for order in query_order:
                            self.order_table.rows.append(
                                DataRow(
                                    cells=[
                                        DataCell(content=self.get_channel(order.order_channel)),
                                        DataCell(Text(order.order_company, color=ft.colors.ON_BACKGROUND)),
                                        DataCell(Text(order.order_number if order.order_reference == None else order.order_reference, color=ft.colors.ON_BACKGROUND)),
                                        DataCell(Text(order.order_customer, color=ft.colors.ON_BACKGROUND)),
                                        DataCell(Text(order.order_shippingMethod, color=ft.colors.ON_BACKGROUND)),
                                        DataCell(Text(order.order_shippingDate.strftime('%d/%m/%Y'), color=ft.colors.ON_BACKGROUND))
                                    ],
                                    selected=False,
                                    data=order.id,
                                    on_select_changed=self.view_order
                                )
                            )
                        self.update()
                        self.page.update()
                        validate_data = True

                    else:
                        validate_none = True

                else:
                    self.order_table.rows.append(
                        DataRow(
                            cells=[
                                DataCell(content=self.get_channel(query_order.order_channel)),
                                DataCell(Text(query_order.order_company, color=ft.colors.ON_BACKGROUND)),
                                DataCell(Text(query_order.order_number if query_order.order_reference == None else query_order.order_reference, color=ft.colors.ON_BACKGROUND)),
                                DataCell(Text(query_order.order_customer, color=ft.colors.ON_BACKGROUND)),
                                DataCell(Text(query_order.order_shippingMethod, color=ft.colors.ON_BACKGROUND)),
                                DataCell(Text(query_order.order_shippingDate.strftime('%d/%m/%Y'), color=ft.colors.ON_BACKGROUND))
                            ],
                            selected=False,
                            data=query_order.id,
                            on_select_changed=self.view_order
                        )
                    )
                    self.update()
                    self.page.update()
                    validate_data = True


        if validate_none==True and validate_data==False:
            self.snackbar.not_found("NÃ£o encontrado.")
            self.page.update()


    def list_shipping(self, channel:str=None, day:int=0):

        """ Lista apenas um pedido de acordo com a pesquisa. """

        self.shipping_table.rows.clear()
        self.pagination.visible = False
        self.update()
        self.page.update()

        query = ANLY(0).query_shippingDay(channel=channel, day=day)

        self.hearder_shipping = ["Canal de Venda", "Conta", "Cod. Pedido", "Pedido", "Forma de Envio", "Data de Envio (ATD)", "Data de Envio (MKP)"]
        self.data_shipping = list()
        self.data_task_gid = list()

        for order in query.iterrows():

            self.data_shipping.append(
                (
                    order[1]['order_channel'],
                    order[1]['order_company'],
                    order[1]['order_number'] if order[1]['order_reference'] == None else order[1]['order_reference'],
                    f'{order[1]['order_number']} - {order[1]['order_customer']}',
                    order[1]['order_shippingMethod'],
                    order[1]['order_shippingDate'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S'),
                    order[1]['order_shippingDateMKP'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S') if type(order[1]['order_shippingDateMKP'].to_pydatetime()) == datetime else '-',
                )
            )

            self.shipping_table.rows.append(
                DataRow(
                    cells=[
                        DataCell(content=self.get_channel(order[1]['order_channel'])),
                        DataCell(Text(order[1]['order_company'], color=ft.colors.ON_BACKGROUND)),
                        DataCell(Text(f"{order[1]['order_number']} - {order[1]['order_customer']}" if order[1]['order_reference'] == None else f"{order[1]['order_reference']} - {order[1]['order_customer']}", color=ft.colors.ON_BACKGROUND)),                        
                        DataCell(Text(order[1]['order_shippingDate'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S'), color=ft.colors.ON_BACKGROUND)),
                        DataCell(Text(order[1]['order_shippingDateMKP'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S') if type(order[1]['order_shippingDateMKP'].to_pydatetime()) == datetime else '-', color=ft.colors.ON_BACKGROUND)),
                        DataCell(content=ft.IconButton(
                            icon=icons.COPY,
                            icon_color=ft.colors.ON_BACKGROUND,
                            icon_size=16,
                            data=f"{order[1]['order_number']} - {order[1]['order_customer']}" if order[1]['order_reference'] == None else f"{order[1]['order_reference']} - {order[1]['order_customer']}",
                            on_click=lambda e: self.page.set_clipboard(e.control.data)
                        ))
                    ],
                    selected=False,
                    data=order[1]['id'],
                    on_select_changed=self.view_order
                )
            )

        self.update()
        self.page.update()
        return None


    def list_shipping_withAsana(self, channel:str, day:int=0):

        """ Lista apenas um pedido de acordo com a pesquisa. """

        query = ANLY(0).query_shippingDay(channel=channel, day=day)

        self.hearder_shippingAsana = ["Canal de Venda", "Conta", "Cod. Pedido", "Pedido", "Forma de Envio", "Data de Envio (ATD)", "Data de Envio (MKP)", "Asana Status"]
        self.data_shippingAsana = list()

        for order in query.iterrows():

            try:
                asana = AsanaAPI()
                task_gid = order[1]['order_task']['gid'][0]
                task_status = None
                get_task = asana.get_a_task(task_gid)

                if 'errors' in get_task:
                    print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsana() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')

                else:
                    for fild in get_task["data"]["custom_fields"]:
                        if fild["gid"] == "1202857995568623":
                            task_status = fild["enum_value"]
                            break

            except Exception as exc:
                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsana() ==> EXCEPTION ASANA TASK: {exc}\n')

            self.data_shippingAsana.append(
                (
                    order[1]['order_channel'],
                    order[1]['order_company'],
                    order[1]['order_number'] if order[1]['order_reference'] == None else order[1]['order_reference'],
                    f'{order[1]['order_number']} - {order[1]['order_customer']}',
                    order[1]['order_shippingMethod'],
                    order[1]['order_shippingDate'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S'),
                    order[1]['order_shippingDateMKP'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S') if type(order[1]['order_shippingDateMKP'].to_pydatetime()) == datetime else '-',
                    task_status["name"] if task_status != None else ""
                )
            )

        self.update()
        self.page.update()
        return None


    def list_shipping_withAsanaShein(self, channel:str, lasday:bool=False):

        """ Lista pedidos da Shein com status do marketplace e do Asana. """

        query = ANLY(0).query_shippingDay(channel=channel, last_day=lasday)

        self.hearder_shippingAsanaShein = ["Pedido", "Cliente", "Data ImpressÃ£o Etiqueta", "Data Envio/Coleta (bipe)", "Nota Fiscal", "Shein Status", "Asana Status"]
        self.data_shippingAsanaShein = list()

        for order in query.iterrows():

            try:
                # OBTEM O STATUS ASANA
                asana = AsanaAPI()
                task_gid = order[1]['order_task']['gid'][0]
                task_status = None
                get_task = asana.get_task(task_gid)

                if 'errors' in get_task:
                    print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShein() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')

                else:
                    for fild in get_task["data"]["custom_fields"]:
                        if fild["gid"] == "1202857995568623":
                            task_status = fild["enum_value"]
                            break

            except Exception as exc:
                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShein() ==> EXCEPTION ASANA TASK: {exc}\n')


            try:
                ## OBTEM STATUS DA SHEIN
                shein = Shein(developer_account=order[1]['order_company']).order_status_pattern(order[1]['order_number'])

            except Exception as exc:
                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShein() ==> EXCEPTION SHEIN API: {exc}\n')


            data_coleta = order[1]['order_shippingDateMKP'].to_pydatetime() + relativedelta(days=1, hour=23, minute=59, second=00)

            self.data_shippingAsanaShein.append(
                (
                    order[1]['order_number'],
                    order[1]['order_customer'],
                    order[1]['order_shippingDateMKP'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S'),
                    data_coleta.strftime('%d/%m/%Y %H:%M:%S'),
                    shein["nota_fiscal"],
                    shein["status"],
                    task_status["name"] if task_status != None else ""
                )
            )

        self.update()
        self.page.update()
        return None


    # def list_shipping_withAsanaShopee1(self):

    #     """ Lista pedidos da Shopee PROCESSADOS com status do marketplace e do Asana. """

    #     company = ['FBF COMUNICACAO', 'FENIX SUBLIMACAO']
    #     self.list_numbers = list()
    #     self.data_shippingAsanaShopee1 = list()
    #     self.hearder_shippingAsanaShopee1 = ["Conta", "Pedido", "Cliente", "Data Envio Shopee", "Shopee Status", "Asana Status"]
        
    #     try:
    #         get_dates = date_differenceCALC(14)
    #         from_date = get_dates['final']
    #         to_date = get_dates['initial'] + relativedelta(days=1)

    #         for cpy in company:
    #             get_shopee_orders = Shopee(cpy).get_order_list(
    #                 filter_time_range_field = "create_time",
    #                 filter_time_from = from_date,
    #                 filter_time_to = to_date,
    #                 filter_order_status = "PROCESSED"
    #             )

    #             for order in get_shopee_orders["response"]["order_list"]:
    #                 self.list_numbers.append(order['order_sn'])
    #             get_shopee_orders = None

    #     except Exception as exc:
    #         print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> EXCEPTION SHOPEE API: {exc}\n')


    #     for number_order in self.list_numbers:

    #         try:
    #             query = ORDER().filter_number(number_order)

    #             # OBTEM O STATUS ASANA
    #             asana = AsanaAPI()
    #             task_gid = query.order_task['gid'][0]
    #             task_status = None
    #             get_task = asana.get_a_task(task_gid)

    #             if 'errors' in get_task:
    #                 print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')

    #             else:
    #                 for fild in get_task["data"]["custom_fields"]:
    #                     if fild["gid"] == "1202857995568623":
    #                         task_status = fild["enum_value"]
    #                         break

    #         except Exception as exc:
    #             print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> EXCEPTION ASANA TASK: {exc}\n')

    #         try:
    #             self.data_shippingAsanaShopee1.append(
    #                 (
    #                     query.order_company,
    #                     query.order_number,
    #                     query.order_customer,
    #                     query.order_shippingDateMKP.strftime('%d/%m/%Y %H:%M:%S'),
    #                     "Processado",
    #                     task_status["name"] if task_status != None else "",
    #                 )
    #             )

    #         except Exception as exc:
    #             print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> EXCEPTION APPEND: {exc}\n')  
    #             self.data_shippingAsanaShopee1.append(
    #                 (
    #                     "",
    #                     number_order,
    #                     "",
    #                     "",
    #                     "Processado",
    #                     "",
    #                 )
    #             )                          

    #     self.update()
    #     self.page.update()
    #     return None


    def list_shipping_withAsanaShopee1(self):
        """ Lista pedidos da Shopee PROCESSADOS com status do marketplace e do Asana. """

        self.list_order_numbers = list()
        self.data_shippingAsanaShopee1 = list()
        self.hearder_shippingAsanaShopee1 = ["Conta", "Pedido", "Cliente", "Produto", "Data Envio Shopee", "Shopee Status", "Asana Status"]

        try:
            get_date_range = date_differenceCALC_30D()

            for company in ['FBF COMUNICACAO', 'FENIX SUBLIMACAO']:
                for data_range in get_date_range:
                    get_shopee_orders = Shopee(company).get_order_list(
                        filter_time_range_field = "create_time",
                        filter_time_from = data_range['end'],
                        filter_time_to = data_range['start'],
                        filter_order_status = "PROCESSED"
                    )

                    for order in get_shopee_orders["response"]["order_list"]:
                        self.list_order_numbers.append(order['order_sn'])
                    get_shopee_orders = None

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> EXCEPTION SHOPEE API: {exc}\n')


        for order_number in self.list_order_numbers:

            try:
                query_order = ORDER().filter_number(order_number)
                query_product = PRODUCT().filter_number(order_number)

                # OBTEM O STATUS ASANA
                asana = AsanaAPI()
                task_gid = query_order.order_task['gid'][0]
                task_status = None
                get_task = asana.get_a_task(task_gid)

                if 'errors' in get_task:
                    print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')

                else:
                    for fild in get_task["data"]["custom_fields"]:
                        if fild["gid"] == "1202857995568623":
                            task_status = fild["enum_value"]
                            break

            except Exception as exc:
                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> EXCEPTION ASANA TASK: {exc}\n')

            try:
                self.data_shippingAsanaShopee1.append(
                    (
                        query_order.order_company,
                        query_order.order_number,
                        query_order.order_customer,
                        "\n".join([f'{product.name} - QTD: {product.qty} UNID' for product in query_product]),
                        query_order.order_shippingDateMKP.strftime('%d/%m/%Y %H:%M:%S'),
                        "Aguardando Postagem/Coleta",
                        task_status["name"] if task_status != None else "",
                    )
                )

            except Exception as exc:
                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee1() ==> EXCEPTION APPEND: {exc}\n')
                self.data_shippingAsanaShopee1.append(
                    (
                        "'-",
                        order_number,
                        "'-",
                        "'-",
                        "'-",
                        "Aguardando Postagem/Coleta",
                        "'-",
                    )
                )

        self.update()
        self.page.update()
        return None


    # def list_shipping_withAsanaShopee2(self, channel:str, lasday:bool=False): ## TODOS OS PEDIDOS

    #     """ Lista pedidos da Shopee com status do marketplace e do Asana. """

    #     self.data_shippingAsanaShopee2 = list()
    #     self.hearder_shippingAsanaShopee2 = ["Conta", "Pedido", "Cliente", "Data Envio Shopee", "Shopee Status", "Asana Status"]

    #     query = ANLY(0).query_shippingDay(channel=channel, last_day=lasday)

    #     for order in query.iterrows():

    #         try:
    #             # OBTEM O STATUS ASANA
    #             asana = AsanaAPI()
    #             task_gid = order[1]['order_task']['gid'][0]
    #             task_status = None
    #             get_task = asana.get_task(task_gid)

    #             if 'errors' in get_task:
    #                 print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')

    #             else:
    #                 for fild in get_task["data"]["custom_fields"]:
    #                     if fild["gid"] == "1202857995568623":
    #                         task_status = fild["enum_value"]
    #                         break

    #         except Exception as exc:
    #             print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION ASANA TASK: {exc}\n')

    #         try:
    #             ## OBTEM STATUS DA SHOPEE
    #             shopee = Shopee(order[1]['order_company']).get_order_detail(order[1]['order_number'])
    #             shopee_status = {"UNPAID": "NÃ£o Pago", "READY_TO_SHIP": "Pronto Para Enviar", "PROCESSED": "Processado", "SHIPPED": "Enviado", "COMPLETED": "ConcluÃ­do", "IN_CANCEL": "Em Cancelamento", "CANCELLED": "Cancelado", "INVOICE_PENDING": "NF Pendente"}

    #         except Exception as exc:
    #             print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION SHOPEE API: {exc}\n')

    #         self.data_shippingAsanaShopee2.append(
    #             (
    #                 order[1]['order_company'],
    #                 order[1]['order_number'],
    #                 order[1]['order_customer'],
    #                 order[1]['order_shippingDateMKP'].to_pydatetime().strftime('%d/%m/%Y %H:%M:%S'),
    #                 shopee_status[shopee['order_status']],
    #                 task_status["name"] if task_status != None else ""
    #             )
    #         )

    #     self.update()
    #     self.page.update()
    #     return None


    def list_shipping_withAsanaShopee2(self, asana_status:bool=True): ## TODOS OS PEDIDOS
        """ Lista pedidos da Shopee com status do marketplace e do Asana. """

        self.data_shippingAsanaShopee2 = list()
        self.hearder_shippingAsanaShopee2 = ["Conta", "Pedido", "Cliente", "Data Envio Shopee", "Shopee Status", "Asana Status", "Status Magis5"]
        total_orders_shopee = dict()

        for company in ['FBF COMUNICACAO', 'FENIX SUBLIMACAO']:
            list_orders_shopee = Shopee(company).get_all_orders()
            total_orders_shopee[company] = f"TOTAL PEDIDOS: {len(list_orders_shopee)}"

            for order in list_orders_shopee:

                ger_order_system = ORDER().filter_number(order[0]) #Obtem as informaÃ§Ãµes do pedido cadastradas no Fadrix System.
                
                shopee_status = {"UNPAID": "NÃ£o Pago", "READY_TO_SHIP": "Preparar Para Enviar", "PROCESSED": "Pronto Para Envio", "SHIPPED": "Enviado", "COMPLETED": "ConcluÃ­do", "IN_CANCEL": "Em Cancelamento", "CANCELLED": "Cancelado", "INVOICE_PENDING": "NF Pendente"}

                magis5hub_status = {
                    'awaiting_payment': 'Aguardando pagamento',
                    'awaiting_approval': 'Aguardando AprovaÃ§Ã£o',
                    'approved': 'Aprovado',
                    'processing_pack_id': 'Processando carrinho',
                    'out_of_stock': 'Sem estoque',
                    'awaiting_stock': 'Aguardando reposiÃ§Ã£o estoque',
                    'awaiting_logistic': 'Aguardando logÃ­stica',
                    'ready_to_print': 'Aguardando separaÃ§Ã£o',
                    'awaiting_invoice': 'Aguardando faturamento',
                    'billed': 'Faturado',
                    'awaiting_send': 'Aguardando envio',
                    'sent': 'Enviado',
                    'delivered': 'Entregue',
                    'delivered_resolved': 'Entregue e resolvido',
                    'not_delivered': 'NÃ£o entregue',
                    'not_delivered_resolved': 'NÃ£o entregue e resolvido',
                    'canceled': 'Cancelado',
                    'canceled_resolved': 'Cancelado e resolvido',
                    'returned_logistic': 'DevoluÃ§Ã£o LogÃ­stica'
                }

                if not ger_order_system:

                    ## --- OBTEM STATUS DA SHOPEE ---
                    try:
                        get_order_shopee = Shopee(company).get_order_detail(order[0])
                        data_order_customer = str(get_order_shopee['response']['order_list'][0]['recipient_address']['name']).title()
                        data_order_shippintDate = datetime.fromtimestamp(get_order_shopee['response']['order_list'][0]['ship_by_date']).strftime('%d/%m/%Y %H:%M:%S')
                        data_order_status = shopee_status[get_order_shopee['response']['order_list'][0]['order_status']]

                    except Exception as exc:
                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION SHOPEE API: {exc}\n')
                        data_order_customer = " --------- "
                        data_order_shippintDate = " --------- "
                        data_order_status = shopee_status[order[1]]

                    task_status = {'name': 'PEDIDO NÃƒO IMPORTADO NO SISTEMA'}

                else:

                    ## --- OBTEM O STATUS ASANA ---
                    try:
                        if asana_status:

                            asana = AsanaAPI()
                            task_gid = ger_order_system.order_task['gid'][0]
                            task_status = None
                            get_task = asana.get_a_task_custom_fields(task_gid)

                            if 'errors' in get_task:
                                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')
                                task_status = {'name': 'ERROR - ASANA API'}

                            else:
                                for fild in get_task["data"]["custom_fields"]:
                                    if fild["gid"] == "1202857995568623":
                                        task_status = {'name': fild["display_value"]}
                                        break

                        else:
                            task_status = {'name': ' ---- '}

                    except Exception as exc:
                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION ASANA TASK: {exc}\n')
                        task_status = {'name': 'EXCEPTION - ASANA API'}

                    try:
                        data_order_customer = ger_order_system.order_customer
                        data_order_shippintDate = ger_order_system.order_shippingDate.strftime('%d/%m/%Y %H:%M:%S')
                        data_order_status = shopee_status[order[1]]

                    except Exception as exc:
                        data_order_customer = ' ---- '
                        data_order_shippintDate = ' ---- '
                        data_order_status = shopee_status[order[1]]

                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION DATA_ORDER INFO: {exc}\n')


                ## --- OBTEM O STATUS MAGIS5 ---
                try:
                    get_order_magis5 = Magis5().get_orders(order_number=order[0])

                    if 'Error' in get_order_magis5:
                        status_magis5 = f'Pedido {order[0]} NÃ£o Encontrado No Magis5' if get_order_magis5['Error']['Code'] == 'NOT_FOUND' else 'ERROR MAGIS5 API'

                    else:

                        if "subStatus" in get_order_magis5:
                            match get_order_magis5["subStatus"]:
                                case "pending_import":
                                    status_magis5 = "Pendente de ImportaÃ§Ã£o"
                                case _:
                                    status_magis5 = get_order_magis5["subStatus"]

                        # elif "subStatusExpedition" in get_order_magis5:
                        #     match get_order_magis5["subStatusExpedition"]:
                        #         case "in_expedition":
                        #             status_magis5 = f"ExpediÃ§Ã£o - {get_order_magis5["expeditionBlock"]}" if "expeditionBlock" in get_order_magis5 else "ExpediÃ§Ã£o"
                        #         case _:
                        #             status_magis5 = get_order_magis5["subStatusExpedition"]

                        status_magis5 = magis5hub_status[get_order_magis5["status"]]

                except Exception as exc:
                    print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION STATUS MAGIS5: {exc}\n')
                    status_magis5 = f'EXCEPTION MAGIS5 API - {exc}'

                ## --- ADICIONA OS DADOS PARA A PLHANILHA ---
                try:
                    self.data_shippingAsanaShopee2.append(
                        (
                            company,
                            order[0],
                            data_order_customer,
                            data_order_shippintDate,
                            data_order_status,
                            task_status["name"] if task_status != None else "",
                            status_magis5
                        )
                    )

                except Exception as exc:
                    print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION APPEND DATA: {exc}\n')

        print(f'\nðŸž ORDER_LIST > list_shipping_withAsanaShopee2() ==> {total_orders_shopee}\n')
        self.update()
        self.page.update()
        return None


    def list_shipping_withAsanaShopeeFLEX(self, asana_status:bool=True): ## TODOS OS PEDIDOS
        """ Lista pedidos da Shopee com logÃ­stica "Entrega Direta (flex)" com status do marketplace e do Asana. """

        self.data_shippingAsanaShopeeFLEX = list()
        self.hearder_shippingAsanaShopeeFLEX = ["Conta", "Pedido", "Cliente", "Data Envio Shopee", "Shopee Status", "Asana Status", "Status Magis5"]
        total_orders_shopee = dict()

        for company in ['FBF COMUNICACAO', 'FENIX SUBLIMACAO']:
            list_orders_shopee = Shopee(company).get_all_orders(flex=True)
            total_orders_shopee[company] = f"TOTAL PEDIDOS: {len(list_orders_shopee)}"

            for order in list_orders_shopee:

                ger_order_system = ORDER().filter_number(order[0]) #Obtem as informaÃ§Ãµes do pedido cadastradas no Fadrix System.

                shopee_status = {
                    "UNPAID": "NÃ£o Pago",
                    "READY_TO_SHIP": "Preparar Para Enviar",
                    "PROCESSED": "Pronto Para Envio",
                    "SHIPPED": "Enviado",
                    "COMPLETED": "ConcluÃ­do",
                    "IN_CANCEL": "Em Cancelamento",
                    "CANCELLED": "Cancelado",
                    "INVOICE_PENDING": "NF Pendente"
                }

                magis5hub_status = {
                    'awaiting_payment': 'Aguardando pagamento',
                    'awaiting_approval': 'Aguardando AprovaÃ§Ã£o',
                    'approved': 'Aprovado',
                    'processing_pack_id': 'Processando carrinho',
                    'out_of_stock': 'Sem estoque',
                    'awaiting_stock': 'Aguardando reposiÃ§Ã£o estoque',
                    'awaiting_logistic': 'Aguardando logÃ­stica',
                    'ready_to_print': 'Aguardando separaÃ§Ã£o',
                    'awaiting_invoice': 'Aguardando faturamento',
                    'billed': 'Faturado',
                    'awaiting_send': 'Aguardando envio',
                    'sent': 'Enviado',
                    'delivered': 'Entregue',
                    'delivered_resolved': 'Entregue e resolvido',
                    'not_delivered': 'NÃ£o entregue',
                    'not_delivered_resolved': 'NÃ£o entregue e resolvido',
                    'canceled': 'Cancelado',
                    'canceled_resolved': 'Cancelado e resolvido',
                    'returned_logistic': 'DevoluÃ§Ã£o LogÃ­stica'
                }

                if not ger_order_system:

                    ## --- OBTEM STATUS DA SHOPEE ---
                    try:
                        get_order_shopee = Shopee(company).get_order_detail(order[0])
                        data_order_customer = str(get_order_shopee['response']['order_list'][0]['recipient_address']['name']).title()
                        data_order_shippintDate = datetime.fromtimestamp(get_order_shopee['response']['order_list'][0]['ship_by_date']).strftime('%d/%m/%Y %H:%M:%S')
                        data_order_status = shopee_status[get_order_shopee['response']['order_list'][0]['order_status']]

                    except Exception as exc:
                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopeeFLEX() ==> EXCEPTION SHOPEE API: {exc}\n')
                        data_order_customer = " --------- "
                        data_order_shippintDate = " --------- "
                        data_order_status = shopee_status[order[1]]

                    task_status = {'name': 'PEDIDO NÃƒO IMPORTADO NO SISTEMA'}

                else:

                    ## --- OBTEM O STATUS ASANA ---
                    try:
                        if asana_status:

                            asana = AsanaAPI()
                            task_gid = ger_order_system.order_task['gid'][0]
                            task_status = None
                            get_task = asana.get_a_task_custom_fields(task_gid)

                            if 'errors' in get_task:
                                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopeeFLEX() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')
                                task_status = {'name': 'ERROR - ASANA API'}

                            else:
                                for fild in get_task["data"]["custom_fields"]:
                                    if fild["gid"] == "1202857995568623":
                                        task_status = {'name': fild["display_value"]}
                                        break

                        else:
                            task_status = {'name': ' ---- '}

                    except Exception as exc:
                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopeeFLEX() ==> EXCEPTION ASANA TASK: {exc}\n')
                        task_status = {'name': 'EXCEPTION - ASANA API'}

                    try:
                        data_order_customer = ger_order_system.order_customer
                        data_order_shippintDate = ger_order_system.order_shippingDate.strftime('%d/%m/%Y %H:%M:%S')
                        data_order_status = shopee_status[order[1]]

                    except Exception as exc:
                        data_order_customer = ' ---- '
                        data_order_shippintDate = ' ---- '
                        data_order_status = shopee_status[order[1]]

                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee2() ==> EXCEPTION DATA_ORDER INFO: {exc}\n')

                ## --- OBTEM O STATUS MAGIS5 ---
                try:
                    get_order_magis5 = Magis5().get_orders(order_number=order[0])

                    if 'Error' in get_order_magis5:
                        status_magis5 = f'Pedido {order[0]} NÃ£o Encontrado No Magis5' if get_order_magis5['Error']['Code'] == 'NOT_FOUND' else 'ERROR MAGIS5 API'

                    else:

                        if "subStatus" in get_order_magis5:
                            match get_order_magis5["subStatus"]:
                                case "pending_import":
                                    status_magis5 = "Pendente de ImportaÃ§Ã£o"
                                case _:
                                    status_magis5 = get_order_magis5["subStatus"]

                        # elif "subStatusExpedition" in get_order_magis5:
                        #     match get_order_magis5["subStatusExpedition"]:
                        #         case "in_expedition":
                        #             status_magis5 = f"ExpediÃ§Ã£o - {get_order_magis5["expeditionBlock"]}" if "expeditionBlock" in get_order_magis5 else "ExpediÃ§Ã£o"
                        #         case _:
                        #             status_magis5 = get_order_magis5["subStatusExpedition"]

                        status_magis5 = magis5hub_status[get_order_magis5["status"]]

                except Exception as exc:
                    print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopeeFLEX() ==> EXCEPTION STATUS MAGIS5: {exc}\n')
                    status_magis5 = f'EXCEPTION MAGIS5 API - {exc}'

                ## --- ADICIONA OS DADOS PARA A PLHANILHA ---
                try:
                    self.data_shippingAsanaShopeeFLEX.append(
                        (
                            company,
                            order[0],
                            data_order_customer,
                            data_order_shippintDate,
                            data_order_status,
                            task_status["name"] if task_status != None else "",
                            status_magis5
                        )
                    )

                except Exception as exc:
                    print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopeeFLEX() ==> EXCEPTION APPEND DATA: {exc}\n')

        print(f'\nðŸž ORDER_LIST > list_shipping_withAsanaShopeeFLEX() ==> {total_orders_shopee}\n')
        self.update()
        self.page.update()
        return None


    def list_shipping_withAsanaShopee3(self): ## PEDIDOS EM ABERTO
        """ Lista pedidos da Shopee com status ------. """

        self.data_shippingAsanaShopee3= list()
        self.hearder_shippingAsanaShopee3 = ["Conta", "Pedido", "Cliente", "Data Envio Shopee", "Shopee Status", "Asana Status"]

        company_list = ['FBF COMUNICACAO', 'FENIX SUBLIMACAO']

        for company in company_list:
            query_order_shopee = Shopee(company).ready_to_ship_list()

            try:
                for order in query_order_shopee:

                    try:
                        query = ORDER().filter_number(order['order_sn'])

                        if query == None:
                            print(f'\nPEDIDO {order['order_sn']} NÃƒO ENCONTRADO NO SISTEMA.\n')
                            self.data_shippingAsanaShopee3.append(
                                (
                                    company,
                                    order['order_sn'],
                                    '**************',
                                    '**************',
                                    "Preparar Envio",
                                    'NÃƒO IMPORTADO NO SISTEMA'
                                )
                            )
                            continue


                        # ## DIA NORMAL -------------

                        today = datetime.now()
                        next_day = today + relativedelta(days=1) if not today.weekday() in [4,5,6] else today + relativedelta(days=3)

                        match query.order_shippingDateMKP:

                            case None:
                                shipping_date = today.strftime('%d/%m/%Y %H:%M:%S')

                            case x if x.date() < next_day.date():
                                shipping_date = query.order_shippingDateMKP.strftime('%d/%m/%Y %H:%M:%S')

                            case y if y.date() == next_day.date() and y.hour < 18:
                                shipping_date = query.order_shippingDateMKP.strftime('%d/%m/%Y %H:%M:%S')

                            case _:
                                continue

                        print(f'\nðŸž ORDER_LIST > list_shipping_withAsanaShopee3 ==> SHIPPING_DATE: {shipping_date}\n')

                        # ## -----------------------


                        # ## FERIADOOO -------------

                        # today = datetime.now()
                        # next_after_holiday = datetime.strptime('02/05/2025 17:59:59', '%d/%m/%Y %H:%M:%S')

                        # match query.order_shippingDateMKP:

                        #     case None:
                        #         shipping_date = today.strftime('%d/%m/%Y %H:%M:%S')

                        #     case x if x.date() < next_after_holiday.date():
                        #         shipping_date = query.order_shippingDateMKP.strftime('%d/%m/%Y %H:%M:%S')

                        #     case y if y.date() == next_after_holiday.date() and y.hour < 18:
                        #         shipping_date = query.order_shippingDateMKP.strftime('%d/%m/%Y %H:%M:%S')

                        #     case _:
                        #         continue

                        # print(f'\nðŸž ORDER_LIST > list_shipping_withAsanaShopee3 ==> SHIPPING_DATE: {shipping_date}\n')

                        # ## -----------------------


                    except Exception as exc:
                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee3() ==> EXCEPTION GET ORDER IN DB {order['order_sn']}: {exc}\n')
                        continue

                    try:
                        # OBTEM O STATUS ASANA
                        asana = AsanaAPI()
                        task_gid = query.order_task['gid'][0]
                        task_status = None
                        get_task = asana.get_a_task(task_gid)

                        if 'errors' in get_task:
                            print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee3() ==> TAREFA "{task_gid}" NÃƒO ENCONTRADA: {get_task}\n')

                        else:
                            for fild in get_task["data"]["custom_fields"]:
                                if fild["gid"] == "1202857995568623":
                                    task_status = fild["enum_value"]
                                    break

                    except Exception as exc:
                        print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee3() ==> EXCEPTION ASANA TASK: {exc}\n')

                    self.data_shippingAsanaShopee3.append(
                        (
                            company,
                            query.order_number,
                            query.order_customer,
                            shipping_date,
                            "Preparar Envio",
                            task_status["name"] if task_status != None else ""
                        )
                    )

            except Exception as exc:
                print(f'\n[ERRO] ORDER_LIST > list_shipping_withAsanaShopee3() ==> EXCEPTION IN FOR COMPANY {company}: {exc}\n')
                continue

        self.update()
        self.page.update()
        return None


    def list_waiting(self, channel:str=None):

        """ Lista pedidos com status de pendÃªncias. """

        try:
            self.pagination.visible = False
            self.update()
            self.page.update()

            query_status = STATUS().filter_all()
            status_dict = dict()
            for status in query_status:
                status_dict[status.name] = status.color

            query_orderStatus = ANLY(0).query_orderStatus(channel=channel)
            for order in query_orderStatus.iterrows():
                self.set_column_waiting.controls.append(
                    Container(
                        content=ft.ListTile(
                            leading=self.get_logo_channel(order[1]['order_channel']),
                            title=Text(f"{order[1]['order_number']} - {order[1]['order_customer']}" if order[1]['order_reference'] == None else f"{order[1]['order_reference']} - {order[1]['order_customer']}", size=15, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                            subtitle=Column(
                                controls=[
                                    Text(value=f'{order[1]['order_channel']} | {order[1]['order_company']}', size=13, weight=ft.FontWeight.W_400, color=ft.colors.ON_BACKGROUND),
                                    Row(
                                        controls=[
                                            Container(
                                                content=Text(value=f'SYSTEM ID #{order[1]['id']}', size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                                bgcolor=ft.colors.TERTIARY_CONTAINER,
                                                border_radius=5,
                                                padding=padding.symmetric(3,5),
                                                margin=margin.symmetric(5),
                                            ),
                                            Container(
                                                content=Text(value=order[1]['order_status'], size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                                bgcolor=status_dict[order[1]['order_status']],
                                                border_radius=5,
                                                padding=padding.symmetric(3,5),
                                                margin=margin.symmetric(5),
                                            ),
                                        ]
                                    )
                                ]
                            ),
                            trailing=ft.IconButton(
                                icon=icons.COPY,
                                icon_color=ft.colors.ON_BACKGROUND,
                                icon_size=16,
                                data=f"{order[1]['order_number']} - {order[1]['order_customer']}" if order[1]['order_reference'] == None else f"{order[1]['order_reference']} - {order[1]['order_customer']}",
                                on_click=lambda e: self.page.set_clipboard(e.control.data)
                            ),
                            data=order[1]['id'],
                            on_click=self.view_order
                        ),
                        bgcolor=ft.colors.BACKGROUND,
                        border_radius=5,
                        margin=margin.symmetric(2,15)
                    )
                )

            query_orderTask = ANLY(self.period).query_sales(channel=channel, limit=None)
            for order in query_orderTask.iterrows():

                try:
                    if "gid" in order[1]['order_task'] and len(order[1]['order_task']["gid"]) == 0:
                        self.set_column_waitingTask.controls.append(
                            Container(
                                content=ft.ListTile(
                                    leading=self.get_logo_channel(order[1]['order_channel']),
                                    title=Text(f"{order[1]['order_number']} - {order[1]['order_customer']}" if order[1]['order_reference'] == None else f"{order[1]['order_reference']} - {order[1]['order_customer']}", size=15, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                    subtitle=Column(
                                        controls=[
                                            Text(value=f'{order[1]['order_channel']} | {order[1]['order_company']}', size=13, weight=ft.FontWeight.W_400, color=ft.colors.ON_BACKGROUND),
                                            Row(
                                                controls=[                                                    
                                                    Container(
                                                        content=Text(value=f'SYSTEM ID #{order[1]['id']}', size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                                        bgcolor=ft.colors.TERTIARY_CONTAINER,
                                                        border_radius=5,
                                                        padding=padding.symmetric(3,5),
                                                        margin=margin.symmetric(5),
                                                    ),
                                                    Container(
                                                        content=Text(value="NÃ£o Enviado P/ Asana", size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                                        bgcolor=ft.colors.ERROR_CONTAINER,
                                                        border_radius=5,
                                                        padding=padding.symmetric(3,5),
                                                        margin=margin.symmetric(5),
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    trailing=ft.IconButton(
                                        icon=icons.COPY,
                                        icon_color=ft.colors.ON_BACKGROUND,
                                        icon_size=16,
                                        data=f"{order[1]['order_number']} - {order[1]['order_customer']}" if order[1]['order_reference'] == None else f"{order[1]['order_reference']} - {order[1]['order_customer']}",
                                        on_click=lambda e: self.page.set_clipboard(e.control.data)
                                    ),
                                    data=order[1]['id'],
                                    on_click=self.view_order
                                ),
                                bgcolor=ft.colors.BACKGROUND,
                                border_radius=5,
                                margin=margin.symmetric(2,15)
                            )
                        )
                except Exception as exc:
                    print(f'\n[ERRO] ORDER_LIST > list_waiting() ==> EXCEPTION QUERY_ORDERTASK: {exc} | PEDIDO: {order[1]['order_number']} - {order[1]['order_task']}\n') ##DEBUG
                    continue

            query_duplicate = ANLY(0).query_duplicate(channel=channel)
            for x, y in query_duplicate.iterrows():
                if y[0] > 1:

                    order = ORDER().filter_number(x)
                    for get_order in order:
                        self.set_column_waitingDuplicate.controls.append(
                            Container(
                                content=ft.ListTile(
                                    leading=self.get_logo_channel(get_order.order_channel),
                                    title=Text(f"{get_order.order_number} - {get_order.order_customer}" if get_order.order_reference == None else f"{get_order.order_reference} - {get_order.order_customer}", size=15, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                    subtitle=Column(
                                        controls=[
                                            Text(value=f'{get_order.order_channel} | {get_order.order_company}', size=13, weight=ft.FontWeight.W_400, color=ft.colors.ON_BACKGROUND),
                                            Row(
                                                controls=[
                                                    Container(
                                                        content=Text(value=f'SYSTEM ID #{get_order.id}', size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                                        bgcolor=ft.colors.TERTIARY_CONTAINER,
                                                        border_radius=5,
                                                        padding=padding.symmetric(3,5),
                                                        margin=margin.symmetric(5),
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    trailing=ft.IconButton(
                                        icon=icons.COPY,
                                        icon_color=ft.colors.ON_BACKGROUND,
                                        icon_size=16,
                                        data=f"{get_order.order_number} - {get_order.order_customer}" if get_order.order_reference == None else f"{get_order.order_reference} - {get_order.order_customer}",
                                        on_click=lambda e: self.page.set_clipboard(e.control.data)
                                    ),
                                    data=get_order.id,
                                    on_click=self.view_order
                                ),
                                bgcolor=ft.colors.BACKGROUND,
                                border_radius=5,
                                margin=margin.symmetric(2,15)
                            )
                        )

            self.update()
            self.page.update()
            return None

        except AttributeError as exc:
            print(f'\n[ERRO] ORDER_LIST > list_waiting() ==> EXCEPTION ATTRIBUTE ERROR: {exc}\n') ##DEBUG
            self.snackbar.not_found("NÃ£o foi encontrado pedidos com pendÃªncias")
            self.update()
            self.page.update()
            return None

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > list_waiting() ==> EXCEPTION: {exc}\n') ##DEBUG
            self.update()
            self.page.update()
            return None


    def load_pagination(self, max_pages, currente, index):

        if self.pagination:
            self.pagination.view_pagination.controls.clear()
            self.pagination.create_pagination(
                max_page=max_pages,
                curr_page=currente,
                index=index,
                funcNum=lambda e: self.list_orders(e.control.text, filter=self.filter_channel, period=self.filter_days),
                funcLast=lambda e: self.list_orders(self.current_page-1, filter=self.filter_channel, period=self.filter_days) if self.current_page > 1 else None,
                funcNext=lambda e: self.list_orders(self.current_page+1, filter=self.filter_channel, period=self.filter_days) if self.current_page < self.max_pages else None,
            )
            self.pagination.visible = True
            self.update()

        else:
            self.pagination = Pagination(self.page)
            self.pagination.create_pagination(
                max_page=max_pages,
                curr_page=currente,
                index=index,
                funcNum=lambda e: self.list_orders(e.control.text, filter=self.filter_channel, period=self.filter_days),
                funcLast=lambda e: self.list_orders(self.current_page-1, filter=self.filter_channel, period=self.filter_days) if self.current_page > 1 else None,
                funcNext=lambda e: self.list_orders(self.current_page+1, filter=self.filter_channel, period=self.filter_days) if self.current_page < self.max_pages else None,
            )
            self.pagination.visible = True
            self.update()


    def import_order(self, e):
        self.page.go("/importar-pedido")


    def view_order(self, e):
        order_id = e.control.data            
        self.page.session.set("order", order_id)
        self.page.go("/visualizar-pedido")


    def dispatch_schedule(self):
        """ Retorna informaÃ§Ãµes de hora de despacho. """

        try:
            list_dispatch = list()

            list_dispatch.append(
                ft.Container(
                    content=ft.Text("HorÃ¡rios De Envio/Coleta Marketplaces", size=18, weight=ft.FontWeight.W_600),
                    padding=ft.padding.symmetric(10, 25)
                )
            )

            for company in ['FENIX SUBLIMACAO', "XDRI SUBLIMACAO"]:

                try:
                    get_schedule = MercadoLivre(company).dispatch_schedule()

                    list_dispatch.append( #MERCADO LIVRE
                        ft.Container(
                            content=ft.ListTile(
                                leading=ft.Image(src='images/system/mercadolivre.png', width=40, border_radius=100),
                                title=ft.Container(
                                    content=ft.Text(value=f"MERCADO LIVRE - {company}", color=ft.colors.PRIMARY, size=15, weight=ft.FontWeight.W_700),
                                    padding=ft.padding.only(bottom=10),
                                    margin=ft.margin.symmetric(7)
                                ),
                                subtitle=ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                ft.Column(
                                                    controls=[
                                                        ft.Text(value="HORÃRIO DE ENVIO/COLETA:", size=12, weight=ft.FontWeight.W_400),
                                                        ft.Text(value=f'Entre {get_schedule["schedule_start"]}h e {get_schedule["schedule_end"]}h' if get_schedule["logistic_type"] == "Mercado Envios Coleta" else f'{get_schedule["schedule_start"]}h', size=15, weight=ft.FontWeight.W_600)
                                                    ],
                                                    spacing=2
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        ft.Text(value="HORÃRIO DE CORTE:", size=12, weight=ft.FontWeight.W_400),
                                                        ft.Text(value=f'Ã€s {get_schedule["cutting_time"]}h', size=15, weight=ft.FontWeight.W_600)
                                                    ],
                                                    spacing=2
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        ft.Text(value="LOGÃSTICA:", size=12, weight=ft.FontWeight.W_400),
                                                        ft.Text(value=f'{get_schedule["logistic_type"]}', size=15, weight=ft.FontWeight.W_600)
                                                    ],
                                                    spacing=2
                                                )
                                            ],
                                            spacing=10
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Column(
                                                    controls=[
                                                        ft.Text(value="TRANSPORTADORA COLETA:", size=12, weight=ft.FontWeight.W_400),
                                                        ft.Text(value=get_schedule['carrier'], size=15, weight=ft.FontWeight.W_600)
                                                    ],
                                                    spacing=2
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        ft.Text(value="MOTORISTA:", size=12, weight=ft.FontWeight.W_400),
                                                        ft.Text(value=get_schedule['driver'], size=15, weight=ft.FontWeight.W_600)
                                                    ],
                                                    spacing=2
                                                ),
                                                ft.Column(
                                                    controls=[
                                                        ft.Text(value="PLACA:", size=12, weight=ft.FontWeight.W_400),
                                                        ft.Text(value=get_schedule['vehicle_plate'], size=15, weight=ft.FontWeight.W_600)
                                                    ],
                                                    spacing=2
                                                )
                                            ],
                                            spacing=10
                                        )                                        
                                    ],
                                    spacing=40,
                                    vertical_alignment=ft.CrossAxisAlignment.START
                                ),
                                trailing=None
                            ),
                            bgcolor=ft.colors.BACKGROUND,
                            border_radius=ft.border_radius.all(10),
                            padding=ft.padding.symmetric(10, 25),
                            col=4
                        )
                    )

                except Exception as exc:
                    print(f'\nERRO AO BUSCAR INFORMAÃ‡Ã•ES DA CONTA MERCADOLIVRE {company} ==> {exc}\n')


            # list_dispatch.append( #MAGALU
            #     ft.Container(
            #         content=ft.ListTile(
            #             leading=ft.Image(src='images/system/magazineluiza.png', width=40, border_radius=100),
            #             title=ft.Container(
            #                 content=ft.Text(value=f"MAGAZINE LUIZA - FENIX SUBLIMACAO", color=ft.colors.PRIMARY, size=15, weight=ft.FontWeight.W_700),
            #                 padding=ft.padding.only(bottom=15),
            #                 margin=ft.margin.symmetric(7)
            #             ),
            #             subtitle=ft.Column(
            #                 controls=[
            #                     ft.Column(
            #                         controls=[
            #                             ft.Text(value="HORÃRIO DE ENVIO/COLETA:", size=12, weight=ft.FontWeight.W_400),
            #                             ft.Text(value=f'Ã€s 15:00h', size=15, weight=ft.FontWeight.W_600)
            #                         ],
            #                         spacing=2
            #                     ),
            #                     ft.Column(
            #                         controls=[
            #                             ft.Text(value="HORÃRIO DE CORTE:", size=12, weight=ft.FontWeight.W_400),
            #                             ft.Text(value=f'-', size=15, weight=ft.FontWeight.W_600)
            #                         ],
            #                         spacing=2
            #                     ),
            #                     ft.Column(
            #                         controls=[
            #                             ft.Text(value="LOGÃSTICA:", size=12, weight=ft.FontWeight.W_400),
            #                             ft.Text(value=f'Magalu Envios Correios', size=15, weight=ft.FontWeight.W_600)
            #                         ],
            #                         spacing=2
            #                     )
            #                 ],
            #                 spacing=10
            #             )
            #         ),
            #         bgcolor=ft.colors.BACKGROUND,
            #         border_radius=ft.border_radius.all(10),
            #         padding=ft.padding.symmetric(10, 25),
            #         col=4
            #     )
            # )

            return list_dispatch

        except:
            print("ERRO DISPATCH SCHEDULE MELI")


    ## FUNCIONS GET DATA ----

    def get_channel(self, name:str):
        channel = CHANNEL().filter_name(name=name)
        return_channel = Row(controls=[Image(width=20, src=channel.icon), Text(channel.name, color=ft.colors.ON_BACKGROUND)])
        return return_channel


    def get_logo_channel(self, name:str) -> Image:
        channel = CHANNEL().filter_name(name=name)
        return Image(width=20, src=channel.icon)


    def clear_search(self, e):
        self.btn_clear.current.visible = False
        self.search_order.current.value = None
        self.tabs_container.current.content.clean()
        self.tabs_container.current.content = self.__tab_list()
        self.tabs_container.current.update()
        self.list_orders(filter=self.filter_channel, period=self.filter_days)
        self.page.update()


    def drop_filter(self, e):

        """ FunÃ§Ã£o para listar os pedidos por canal de venda especÃ­fico. """

        self.filter_channel = e.control.text if e.control.text != "Limpar Filtro" else None
        self.text_channel.current.value = self.filter_channel
        self.text_channel.current.update()

        match self.tabs_module_order.selected_index:

            case 0:
                self.tabs_container.current.content.clean()
                self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
                self.tabs_container.current.update()

                self.pagination = Pagination(self.page)
                self.list_orders(filter=self.filter_channel, period=self.filter_days)
                self.tabs_container.current.content = self.__tab_list()
                self.tabs_container.current.update()
                self.page.update()

            # case 1:
            #     self.tabs_container.current.content.clean()
            #     self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
            #     self.tabs_container.current.update()

            #     self.tabs_container.current.content = self.__tab_waiting()
            #     self.tabs_container.current.update()
            #     self.page.update()

            case 1:
                self.tabs_container.current.content.clean()
                self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
                self.tabs_container.current.update()

                self.tabs_container.current.content = self.__tab_listShipping(self.filter_yesterday)
                self.tabs_container.current.update()
                self.page.update()

            case 2:
                self.tabs_container.current.content.clean()
                self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
                self.tabs_container.current.update()

                self.tabs_container.current.content = self.__tab_dashboard()
                self.tabs_container.current.update()
                self.page.update()


    def drop_filterDays(self, e):

        """ FunÃ§Ã£o para listar os pedidos por perÃ­odo especÃ­fico. """

        self.text_days.current.value = e.control.text if e.control.text != "Limpar Filtro" else None
        self.text_days.current.update()

        last_day=False
        next_day=False

        match e.control.text:
            case "Ontem":
                self.filter_days = 1 
                last_day=True
                next_day=False
            case "AmanhÃ£":
                self.filter_days = -1 
                last_day=False
                next_day=True             
            case "7 dias":
                self.filter_days = 7
                last_day=False
                next_day=False
            case "15 dias":
                self.filter_days = 15
                last_day=False
                next_day=False
            case "30 dias":
                self.filter_days = 30
                last_day=False
                next_day=False
            case "60 dias":
                self.filter_days = 60
                last_day=False
                next_day=False
            case "90 dias":
                self.filter_days = 90
                last_day=False
                next_day=False
            case "180 dias":
                self.filter_days = 180
                last_day=False
                next_day=False                
            case _ :
                self.filter_days = 60
                last_day=False
                next_day=False

        match self.tabs_module_order.selected_index:

            case 0:
                self.tabs_container.current.content.clean()
                self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
                self.tabs_container.current.update()
                self.page.update()

                self.pagination = Pagination(self.page)
                self.list_orders(filter=self.filter_channel, period=self.filter_days)
                self.tabs_container.current.content = self.__tab_list()
                self.tabs_container.current.update()
                self.page.update()

            case 1:
                self.tabs_container.current.content.clean()
                self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
                self.tabs_container.current.update()
                self.page.update()

                filter_day = self.filter_days if last_day == True or next_day == True else 0
                self.tabs_container.current.content = self.__tab_listShipping(day_filter=filter_day)
                self.tabs_container.current.update()
                self.page.update()

            case 2:
                self.tabs_container.current.content.clean()
                self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
                self.tabs_container.current.update()
                self.page.update()

                self.tabs_container.current.content = self.__tab_dashboard()
                self.tabs_container.current.update()
                self.page.update()

            case _:
                None


    def hover_filters(self, e):
        e.control.bgcolor = ft.colors.PRIMARY_CONTAINER if not e.control.bgcolor else None
        e.control.update()
        self.page.update()

    ## END ----



    def report_dailyshipments(self):

        self.alert.progress_dialog("Gerando Planilha ...")
        self.page.dialog = self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        try:
            self.list_shipping(channel=self.filter_channel)

            path_directory = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/daily_shipments"
            title = f'FSYS_DAILYSHIPMENTS__{self.filter_channel if self.filter_channel != None else "GERAL"}_{DATE().strftime('%Y-%m-%d %H.%M.%S')}'.upper()
            excel = tablib.Dataset(*self.data_shipping, headers=self.hearder_shipping)
            excel.title = title

            with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            self.alert.open=False
            self.page.update()
            self.page.dialog.clean()
            
            print(f'\nâ¬‡ DOWNLOAD REPORT => {title}, POR {self.user_system["name"]}\n')
            self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

            notice = NoticeControl(
                page=self.page,
                topic="RelatÃ³rio",
                title=f"Downlod da Planilha Envios {self.filter_channel if self.filter_channel != None else "GERAL"} {DATE().date().strftime('%d/%m')} DisponÃ­vel!",
                messagem=f"Sua planilha com o relatÃ³rio de envios do pedidos jÃ¡ estÃ¡ disponÃ­vel.\n\nBAIXE AGORA!",
                action="Download",
                user=self.user_system["name"],
                link=f'{path_directory}/{title}.xlsx',
                date=DATE()
            )

            save_notice = notice.create_notice()

            if save_notice:
                self.page.pubsub.send_all(notice.return_notice())
            else:
                print(f'\n[ERRO] ORDER_LIST > report_dailyshipments() ==> NÃƒO FOI POSSÃVEL CRIAR A NOTIFICAÃ‡ÃƒO.\n')

            self.page.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > report_dailyshipments() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def report_dailyshipments_with_asana(self):

        if self.filter_channel == None:
            self.snackbar.warning("RelatÃ³rio disponÃ­vel apenas para um (1) canal de venda por vez. Use os filtros para selecionar um canal de venda (marketplace).")
            self.page.update()
            return None

        self.alert.progress_dialog("Gerando Planilha ...")
        self.page.dialog = self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        try:
            filter_day = self.filter_days if self.filter_days == 1 or self.filter_days == -1 else 0
            self.list_shipping_withAsana(self.filter_channel, filter_day)

            path_directory = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/daily_shipments"
            title = f'FSYS_DAILYSHIPMENTS__{self.filter_channel}_{DATE().strftime('%Y-%m-%d %H.%M.%S')}'.upper()
            excel = tablib.Dataset(*self.data_shippingAsana, headers=self.hearder_shippingAsana)
            excel.title = title

            with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            self.alert.open=False
            self.page.update()
            self.page.dialog.clean()

            print(f'\nâ¬‡ DOWNLOAD REPORT WITH ASANA INFO => {title}, POR {self.user_system["name"]}\n')

            self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

            notice = NoticeControl(
                page=self.page,
                topic="RelatÃ³rio",
                title=f"Downlod da Planilha Envios C/ Asana {self.filter_channel} {DATE().date().strftime('%d/%m')} DisponÃ­vel!",
                messagem=f"Sua planilha com o relatÃ³rio de envios do pedidos jÃ¡ estÃ¡ disponÃ­vel.\n\nBAIXE AGORA!",
                action="Download",
                user=self.user_system["name"],
                link=f'{path_directory}/{title}.xlsx',
                date=DATE()
            )

            save_notice = notice.create_notice()

            if save_notice:
                self.page.pubsub.send_all(notice.return_notice())
            else:
                print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana() ==> NÃƒO FOI POSSÃVEL CRIAR A NOTIFICAÃ‡ÃƒO.\n')

            self.page.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def report_dailyshipments_with_asana_shein(self):

        if self.filter_channel != "Shein":
            self.snackbar.warning("Este relatÃ³rio estÃ¡ disponÃ­vel apenas para o marketplace da SHEIN. Por favor, selecione o marketplace correto nos filtros de pesquisa.")
            self.page.update()
            return None

        self.alert.progress_dialog("Gerando Planilha ...")
        self.page.dialog = self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        #try:
        self.list_shipping_withAsanaShein("Shein", self.filter_yesterday)

        path_directory = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/daily_shipments"
        title = f'FSYS_DAILYSHIPMENTS__SHEIN-FULL_{DATE().strftime('%Y-%m-%d %H.%M.%S')}'.upper()
        excel = tablib.Dataset(*self.data_shippingAsanaShein, headers=self.hearder_shippingAsanaShein)
        excel.title = title

        with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
            f.write(excel.export('xlsx'))

        self.alert.open=False
        self.page.update()
        self.page.dialog.clean()

        print(f'\nâ¬‡ DOWNLOAD REPORT SHEIN-FULL => {title}, POR {self.user_system["name"]}\n')

        self.snackbar.sucess(msg="Planilha gerada, seu download comeÃ§arÃ¡ em breve.")
        self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

        notice = NoticeControl(
            page=self.page,
            topic="RelatÃ³rio",
            title=f"Downlod da Planilha SHEIN FULL {self.filter_channel} {DATE().date().strftime('%d/%m')} DisponÃ­vel!",
            messagem=f"Sua planilha com o relatÃ³rio de envios do pedidos jÃ¡ estÃ¡ disponÃ­vel.\n\nBAIXE AGORA!",
            action="Download",
            user=self.user_system["name"],
            link=f'{path_directory}/{title}.xlsx',
            date=DATE()
        )

        save_notice = notice.create_notice()

        if save_notice:
            self.page.pubsub.send_all(notice.return_notice())
        else:
            print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shein() ==> NÃƒO FOI POSSÃVEL CRIAR A NOTIFICAÃ‡ÃƒO.\n')

        self.page.update()

        # except Exception as exc:
        #     print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shein() ==> EXCEPTION: {exc}\n')
        #     self.snackbar.internal_error()
        #     self.page.update()


    def report_dailyshipments_with_asana_shopee1(self):

        if self.filter_channel != "Shopee":
            self.snackbar.warning("Este relatÃ³rio estÃ¡ disponÃ­vel apenas para o marketplace da SHOPEE. Por favor, selecione o marketplace correto nos filtros de pesquisa.")
            self.page.update()
            return None

        self.alert.progress_dialog("Gerando Planilha ...")
        self.page.dialog = self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        try:
            self.list_shipping_withAsanaShopee1()

            path_directory = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/daily_shipments"
            title = f'FSYS_DAILYSHIPMENTS__SHOPEE-FULL_PROCESSED_{DATE().strftime('%Y-%m-%d %H.%M.%S')}'.upper()
            excel = tablib.Dataset(*self.data_shippingAsanaShopee1, headers=self.hearder_shippingAsanaShopee1)
            excel.title = title

            with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            self.alert.open=False
            self.page.update()
            self.page.dialog.clean()

            print(f'\nâ¬‡ DOWNLOAD REPORT SHOPEE-FULL_PROCESSED => {title}, POR {self.user_system["name"]}\n')

            self.snackbar.sucess(msg="Planilha gerada, seu download comeÃ§arÃ¡ em breve.")
            self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

            notice = NoticeControl(
                page=self.page,
                topic="RelatÃ³rio",
                title=f"Downlod da Planilha SHOPEE FULL PROCESSED {DATE().date().strftime('%d/%m')} DisponÃ­vel!",
                messagem=f"Sua planilha com o relatÃ³rio de envios do pedidos jÃ¡ estÃ¡ disponÃ­vel.\n\nBAIXE AGORA!",
                action="Download",
                user=self.user_system["name"],
                link=f'{path_directory}/{title}.xlsx',
                date=DATE()
            )

            save_notice = notice.create_notice()

            if save_notice:
                self.page.pubsub.send_all(notice.return_notice())
            else:
                print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopee1() ==> NÃƒO FOI POSSÃVEL CRIAR A NOTIFICAÃ‡ÃƒO.\n')

            self.page.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopee1() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def report_dailyshipments_with_asana_shopee2(self):

        """ RelatÃ³rio dos pedidos Shopee para envio no dia, com informaÃ§Ãµes do Asana e estatus da Shopee"""

        if self.filter_channel != "Shopee":
            self.snackbar.warning("Este relatÃ³rio estÃ¡ disponÃ­vel apenas para o marketplace da SHOPEE. Por favor, selecione o marketplace correto nos filtros de pesquisa.")
            self.page.update()
            return None

        self.alert.progress_dialog("Gerando Planilha ...")
        self.page.dialog = self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        try:
            self.list_shipping_withAsanaShopee2()

            path_directory = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/daily_shipments"
            title = f'FSYS_DAILYSHIPMENTS__SHOPEE-FULL_{DATE().strftime('%Y-%m-%d %H.%M.%S')}'.upper()
            excel = tablib.Dataset(*self.data_shippingAsanaShopee2, headers=self.hearder_shippingAsanaShopee2)
            excel.title = title

            with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            self.alert.open=False
            self.page.update()
            self.page.dialog.clean()

            print(f'\nâ¬‡ DOWNLOAD REPORT SHOPEE-FULL => {title}, POR {self.user_system["name"]}\n')

            self.snackbar.sucess(msg="Planilha gerada, seu download comeÃ§arÃ¡ em breve.")
            self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

            notice = NoticeControl(
                page=self.page,
                topic="RelatÃ³rio",
                title=f"Downlod da Planilha SHOPEE FULL {DATE().date().strftime('%d/%m')} DisponÃ­vel!",
                messagem=f"Sua planilha com o relatÃ³rio de envios de pedidos jÃ¡ estÃ¡ disponÃ­vel.\n\nBAIXE AGORA!",
                action="Download",
                user=self.user_system["name"],
                link=f'{path_directory}/{title}.xlsx',
                date=DATE()
            )

            save_notice = notice.create_notice()

            if save_notice:
                self.page.pubsub.send_all(notice.return_notice())
            else:
                print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopee2() ==> NÃƒO FOI POSSÃVEL CRIAR A NOTIFICAÃ‡ÃƒO.\n')

            self.page.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopee2() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def report_dailyshipments_with_asana_shopeeFLEX(self):
        """ RelatÃ³rio dos pedidos Shopee para envio no dia de pedidos "Entrega Direta (flex)", com informaÃ§Ãµes do Asana e estatus da Shopee"""

        if self.filter_channel != "Shopee":
            self.snackbar.warning("Este relatÃ³rio estÃ¡ disponÃ­vel apenas para o marketplace da SHOPEE. Por favor, selecione o marketplace correto nos filtros de pesquisa.")
            self.page.update()
            return None

        self.alert.progress_dialog("Gerando Planilha Shopee Entrega Direta ...")
        self.page.dialog = self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        try:
            self.list_shipping_withAsanaShopeeFLEX()

            path_directory = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/daily_shipments"
            title = f'FSYS_DAILYSHIPMENTS__SHOPEE-ENTREGA-DIRETA_{DATE().strftime('%Y-%m-%d %H.%M.%S')}'.upper()
            excel = tablib.Dataset(*self.data_shippingAsanaShopeeFLEX, headers=self.hearder_shippingAsanaShopeeFLEX)
            excel.title = title

            with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            self.alert.open=False
            self.page.update()
            self.page.dialog.clean()

            print(f'\nâ¬‡ DOWNLOAD REPORT SHOPEE ENTREGA DIRETA => {title}, POR {self.user_system["name"]}\n')

            #self.snackbar.sucess(msg="Planilha gerada, seu download comeÃ§arÃ¡ em breve.")
            self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

            notice = NoticeControl(
                page=self.page,
                topic="RelatÃ³rio",
                title=f"Downlod da Planilha SHOPEE FULL {DATE().date().strftime('%d/%m')} DisponÃ­vel!",
                messagem=f"Sua planilha com o relatÃ³rio de envios de pedidos jÃ¡ estÃ¡ disponÃ­vel.\n\nBAIXE AGORA!",
                action="Download",
                user=self.user_system["name"],
                link=f'{path_directory}/{title}.xlsx',
                date=DATE()
            )

            save_notice = notice.create_notice()

            if save_notice:
                self.page.pubsub.send_all(notice.return_notice())
            else:
                print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopeeFLEX() ==> NÃƒO FOI POSSÃVEL CRIAR A NOTIFICAÃ‡ÃƒO.\n')

            self.page.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopeeFLEX() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def report_dailyshipments_with_asana_shopee3(self):

        """ RelatÃ³rio dos pedidos Shopee -------. """

        if self.filter_channel != "Shopee":
            self.snackbar.warning("Este relatÃ³rio estÃ¡ disponÃ­vel apenas para o marketplace da SHOPEE. Por favor, selecione o marketplace correto nos filtros de pesquisa.")
            self.page.update()
            return None

        self.alert.progress_dialog("Gerando Planilha ...")
        self.page.dialog = self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        try:
            self.list_shipping_withAsanaShopee3()

            path_directory = "D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/daily_shipments"
            title = f'FSYS_DAILYSHIPMENTS__SHOPEE-FULL-3_{DATE().strftime('%Y-%m-%d %H.%M.%S')}'.upper()
            excel = tablib.Dataset(*self.data_shippingAsanaShopee3, headers=self.hearder_shippingAsanaShopee3)
            excel.title = title

            with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            self.alert.open=False
            self.page.update()
            self.page.dialog.clean()

            print(f'\nâ¬‡ DOWNLOAD REPORT SHOPEE-FULL => {title}, POR {self.user_system["name"]}\n')

            self.snackbar.sucess(msg="Planilha gerada, seu download comeÃ§arÃ¡ em breve.")
            self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

            notice = NoticeControl(
                page=self.page,
                topic="RelatÃ³rio",
                title=f"Downlod da Planilha SHOPEE FULL 3 {DATE().date().strftime('%d/%m')} DisponÃ­vel!",
                messagem=f"Sua planilha com o relatÃ³rio de envios de pedidos jÃ¡ estÃ¡ disponÃ­vel.\n\nBAIXE AGORA!",
                action="Download",
                user=self.user_system["name"],
                link=f'{path_directory}/{title}.xlsx',
                date=DATE()
            )

            save_notice = notice.create_notice()

            if save_notice:
                self.page.pubsub.send_all(notice.return_notice())
            else:
                print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopee3() ==> NÃƒO FOI POSSÃVEL CRIAR A NOTIFICAÃ‡ÃƒO.\n')

            self.page.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_LIST > report_dailyshipments_with_asana_shopee3() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


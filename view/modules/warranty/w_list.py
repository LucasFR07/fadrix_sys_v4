import flet as ft
from flet import (
    Page, UserControl, DataTable, DataColumn, DataRow, DataCell, Container, Column, Row, Ref, Text, TextStyle, TextField, Divider, MainAxisAlignment, Icon, Image, ScrollMode, icons, margin, padding, alignment, border_radius, Tabs, Tab, PopupMenuButton, PopupMenuItem )


import math
from datetime import datetime
import tablib

## CONEXÃO COM DADOS
from data.repository.warranty import WarrantyRepository as WARRANTY
from data.repository.warranty_product import WarrantyProductRepository as WARRANTY_PROD
from data.repository.saleschannel import SalesChannelRepository as CHANNEL
from data.repository.status import StatusRepository as STATUS

## CONTROLES DO SISTEMA
from controllers.date_control import date_create as DATE

## COMPONENTES TEMPLATE
from view.component.buttons import ButtonsComponents as BUTTON
from view.component.dialog import Dialog
from view.component.snackbar import SnackBar_PATTERNS

## WIDGET TEMPLATE
from view.widget.pagination import Pagination


class WarrantyList(UserControl):

    def __init__(self, page:Page):
        super().__init__()
        self.page = page

        ## WIDGETS ---------

        self.snackbar = SnackBar_PATTERNS(self.page)
        self.alert = Dialog(self.page)

        ## ---------


        ## VARIÁVEIS ---------

        self.pagination = None
        self.filter_channel = None
        self.filter_days = None

        self.tabs_warranty = Ref[Tabs]
        self.tabs_container = Ref[Container]()
        self.search_warranty = Ref[TextField]()
        self.search_search = Ref[Container]()

        self.text_channel = Ref[Text]()
        self.text_days = Ref[Text]()

        ## ---------

        self.warranty_table = DataTable(
            sort_column_index=0,
            sort_ascending=True,
            heading_row_color= ft.colors.SURFACE_VARIANT,
            heading_row_height=45,
            data_row_color={"hovered": ft.colors.INVERSE_PRIMARY},
            divider_thickness=0,
            column_spacing=50,
            columns=[
                DataColumn(
                    Text("ID Garantia", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Identificador da Garantia no Fadrix System",
                ),
                DataColumn(
                    Text("Canal de Venda", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Canal de Venda",
                ),
                DataColumn(
                    Text("Número do Pedido", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Número do Pedido"
                ),
                DataColumn(
                    Text("Cliente", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Nome do Cliente",
                ),
                DataColumn(
                    Text("Status", color=ft.colors.ON_BACKGROUND, weight="w700", size=14),
                    tooltip="Status da Garantia",
                ),
            ],
            width=2600,
        )

        self.__content_warrantys()



    def build(self):

        view = Container(
            content=Column(
                controls=[

                    #HEADER CONTAINER
                    Container(
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
                                                                content=Icon(name=icons.SHIELD_OUTLINED, size=25, color=ft.colors.ON_BACKGROUND),
                                                                width=40,
                                                                height=40,
                                                                bgcolor=ft.colors.INVERSE_PRIMARY,
                                                                border_radius=border_radius.all(10)
                                                            ),
                                                            Text(value="Garantia de Vendas", size=25, weight="w700", color=ft.colors.ON_BACKGROUND)
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            Column(
                                                controls=[
                                                    Row(
                                                        controls=[
                                                            BUTTON(page=self.page, icon="add", text="NOVA", style="small", color="primary", event=self.new_warranty),
                                                            # BUTTON(page=self.page, icon="print", text="imprimir", style="small", color="primary").outline(),
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
                                            Tabs(
                                                selected_index=0,
                                                animation_duration=300,
                                                tabs=[
                                                    Tab(
                                                        tab_content=Row(
                                                            controls=[
                                                                Icon(name=icons.LIST_ROUNDED, color=ft.colors.ON_BACKGROUND, size=16),
                                                                Text(value="Garantias", color=ft.colors.ON_BACKGROUND, size=14)
                                                            ],
                                                        )
                                                    ),
                                                ],
                                                indicator_color=ft.colors.PRIMARY,
                                                divider_color=ft.colors.BACKGROUND,
                                                height=37,
                                                width=600,
                                                on_change=self.change_tabs,
                                                ref=self.tabs_warranty
                                            ),
                                            Row(
                                                controls=[
                                                    # Column(
                                                    #     controls=[
                                                    #         Row(
                                                    #             controls=[
                                                    #                 TextField(
                                                    #                     # icon=icons.SEARCH_OUTLINED, 
                                                    #                     hint_text="pesquisar",
                                                    #                     hint_style=TextStyle(italic=True, size=14),
                                                    #                     text_style=TextStyle(size=14, weight="w600"),
                                                    #                     color=ft.colors.ON_BACKGROUND,
                                                    #                     bgcolor=ft.colors.SURFACE_VARIANT,
                                                    #                     border_color=ft.colors.OUTLINE,
                                                    #                     border_radius=5,
                                                    #                     focused_color=ft.colors.PRIMARY,
                                                    #                     focused_border_color=ft.colors.PRIMARY,
                                                    #                     content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                    #                     width=250,
                                                    #                     height=35,
                                                    #                     ref=self.search_warranty,
                                                    #                     # on_submit=self.__tab_order
                                                    #                 ),
                                                    #                 Container(
                                                    #                     content=BUTTON(page=self.page, text="limpar", style="small", color="info", event=print()).outline(),
                                                    #                     visible=False,
                                                    #                     #ref=self.btn_clear_search
                                                    #                 ),
                                                    #             ]
                                                    #         )
                                                    #     ]
                                                    # ),

                                                    # FILTROS DE PESQUISA
                                                    # Column(
                                                    #     controls=[
                                                    #         PopupMenuButton(
                                                    #             content=Container(
                                                    #                 content=Row([Icon(icons.FILTER_LIST, color=ft.colors.PRIMARY), Text(value=None, color=ft.colors.PRIMARY, ref=self.text_channel)]),
                                                    #                 border_radius=border_radius.all(50),
                                                    #                 padding=padding.symmetric(6,10),
                                                    #                 on_hover=self.hover_filters
                                                    #             ),                                                                
                                                    #             tooltip="Filtrar por Canal de Venda", 
                                                    #             items=[
                                                    #                 PopupMenuItem(icon=icons.STOREFRONT, text="Amazon", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.STOREFRONT, text="Americanas", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.STOREFRONT, text="Magazine Luiza", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.STOREFRONT, text="Mercado Livre", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.STOREFRONT, text="Shein", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.STOREFRONT, text="Shopee", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.STOREFRONT, text="Prestashop", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(),
                                                    #                 PopupMenuItem(icon=icons.CLEAR_ALL, text="Limpar Filtro", on_click=lambda e: print()),
                                                    #             ],
                                                    #         ),
                                                    #     ]
                                                    # ),
                                                    # Column(
                                                    #     controls=[
                                                    #         PopupMenuButton(
                                                    #             content=Container(
                                                    #                 content=Row([Icon(icons.CALENDAR_MONTH, color=ft.colors.PRIMARY), Text(value=None, color=ft.colors.PRIMARY, ref=self.text_days)]),
                                                    #                 border_radius=border_radius.all(50),
                                                    #                 padding=padding.symmetric(6,10),
                                                    #                 on_hover=self.hover_filters
                                                    #             ),
                                                    #             tooltip="Filtrar por Período",
                                                    #             items=[
                                                    #                 PopupMenuItem(icon=icons.CALENDAR_TODAY, text="7 dias", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.CALENDAR_TODAY, text="15 dias", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.CALENDAR_TODAY, text="30 dias", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.CALENDAR_TODAY, text="60 dias", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(icon=icons.CALENDAR_TODAY, text="90 dias", on_click=lambda e: print()),
                                                    #                 PopupMenuItem(),
                                                    #                 PopupMenuItem(icon=icons.CLEAR_ALL, text="Limpar Filtro", on_click=lambda e: print())
                                                    #             ],
                                                    #         ),
                                                    #     ]
                                                    # ),

                                                ]
                                            ),
                                        ],
                                        alignment="spaceBetween"
                                    ),
                                    margin=margin.symmetric(vertical=10, horizontal=25)
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



    ## TABS ---------

    def __tab_list(self):

        self.tabs_warranty.current.selected_index=0

        return Column(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=self.warranty_table,
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
                        # controls=[self.pagination],
                        alignment=MainAxisAlignment.CENTER
                    ),
                    height=43,
                    alignment=alignment.center,
                    padding=padding.symmetric(vertical=10),
                    margin=margin.symmetric(vertical=15)
                )
            ]
        )


    def change_tabs(self, e):

        if self.tabs_container.current.content != None:
            self.tabs_container.current.content.clean()
            self.tabs_container.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
            self.tabs_container.current.update()

        match e.control.selected_index:

            case 0:
                self.pagination = Pagination(self.page)
                self.__content_warrantys()
                self.tabs_container.current.content = self.__tab_list()
                self.tabs_container.current.update()

    ## ---------



    ## CONTENTS ---------

    def __content_warrantys(self, currentPage=1, filter_channel:str=None):

        """ Exibe a listagem de garantias registradas no sistema. """

        try:

            self.warranty_table.rows.clear()
            self.current_page = currentPage
            self.limite_query = 25 * self.current_page


            if filter_channel != None:
                self.get_warrantys = WARRANTY().filter_channel(filter_channel)
                total_query = len(self.get_warrantys)

                if total_query == 0:
                    self.snackbar.not_found(f"Não encontrado Garantias no canal de venda {filter_channel}.")
                    self.page.update()
                    return None

            else:
                self.get_warrantys = WARRANTY().filter_all()                
                total_query = len(self.get_warrantys)

                if total_query == 0:
                    self.snackbar.not_found("Nenhuma garantia foi encontrada. Adicione uma para ser exibida nessa listagem!")
                    self.page.update()
                    return None

            max_pages = math.ceil(total_query/self.limite_query)
            offset_query = 25 * (self.current_page - 1)
            index = max_pages if max_pages <= 4 else 4

            if self.current_page == 1:
                self.response_orders = self.get_warrantys[0:self.limite_query]
            else:
                self.response_orders = self.get_warrantys[offset_query+1:self.limite_query]


            for war in self.get_warrantys:
                self.warranty_table.rows.append(
                    DataRow(
                        cells=[
                            DataCell(content=self.__get_channel(name=war.order_channel)),
                            DataCell(Text(value=war.order_ref, color=ft.colors.ON_BACKGROUND)),
                            DataCell(Text(value=war.order_buyer, color=ft.colors.ON_BACKGROUND)),
                            DataCell(Text(value=war.status, color=ft.colors.ON_BACKGROUND)),
                            DataCell(Text(value=f'G-{war.id}', color=ft.colors.ON_BACKGROUND)),
                        ],
                        selected=False,
                        data=war.id,
                        # on_select_changed=self.view_order
                    )
                )

            self.update()
            self.page.update()


        except Exception as exc:
            print(exc)


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

    ## ---------



    ## REDIRECTS ---------

    def new_warranty(self, e):
        self.page.go("/garantias/nova")

    ## ---------



    ## GET DATA ----

    def __get_channel(self, name:str):
        channel = CHANNEL().filter_name(name=name)
        return Row(controls=[Image(width=20, src=channel.icon), Text(channel.name, color=ft.colors.ON_BACKGROUND)])

    ## ---------

import flet as ft
from flet import (
    Page, UserControl, Ref,
    Column, Row, ResponsiveRow, Container, Divider,
    Text, TextStyle, TextField, Dropdown, IconButton, Image, ImageFit,
    Icon, MainAxisAlignment, CrossAxisAlignment,
    dropdown, icons, margin, padding, alignment, border_radius
)


## CONEXÃO COM DADOS
from data.repository.status import StatusRepository as STATUS
from data.repository.orderV2 import OrderRepositoryV2 as ORDER_REP
from data.repository.order_product import OrderProductRepository as ORDER_PRD
from data.repository.commentsV2 import CommentsV2Repository as NOTE
from data.repository.userV2 import UserV2Repository as USER
from data.repository.company import CompanyRepository as COMPANY
from data.repository.saleschannel import SalesChannelRepository as SALES
from data.repository.carrier import CarrierRepository as CARRIER
from sqlalchemy import null

## CONTROLES DO SISTEMA
from controllers.date_control import date_create as DATE
from controllers.order_control import OrderControl as ORDER
from controllers.task_control import TaskControl as TASK
from datetime import datetime
from pathlib import Path
import shutil, os

## COMPONENTES TEMPLATE
from view.component.buttons import ButtonsComponents as btn
from view.component.dialog import Dialog
from view.component.snackbar import SnackBar_PATTERNS
from view.modules.notes.notes_template import NotesTemplate
from view.modules.asana.asana_template import AsanaTemplate
from view.modules.tracking.tracking_template import TrackingTemplate
from view.modules.magis5.magis5_template import Magis5Template



## WIDGET TEMPLATE
from view.widget.calendar import Calendar

## API
from source.api.asanaApi import AsanaAPI
from source.api.magis5 import Magis5


class OrderView(UserControl):

    def __init__(self, page:Page):
        super().__init__()
        self.page = page

        # INFORMAÇÕES DE SESSÃO:
        self.user_system = self.page.client_storage.get("user_info")
        self.order = self.page.session.get("order")
        ## ---------

        ## WIDGETS:
        self.alert = Dialog(self.page)
        self.snackbar = SnackBar_PATTERNS(self.page)
        self.create_box_comment = None
        ## ---------

        ## VARIÁVEIS (REFs):
        self.order_channel = Ref[TextField]()
        self.order_company = Ref[TextField]()
        self.order_date = Ref[TextField]()
        self.order_shippingMethod = Ref[TextField]()
        self.order_shippingDate = Ref[TextField]()
        self.order_user = Ref[TextField]()
        self.order_customer = Ref[TextField]()
        self.order_customerNickname = Ref[TextField]()
        self.order_shippingAddress = Ref[TextField]()
        self.product_column = Ref[Column]()
        self.products = Ref[Column]()
        self.insert_text = Ref[TextField]()
        self.check_asana = Ref[ft.Switch]()
        self.tabs_box = Ref[ft.Tabs]()

        self.product_divider = Ref[ft.DataTable]()
        self.copy_products = list()

        self.asana_task_create = None

        ## ---------


        if self.order != None:
            self.get_order(self.order)
            self.__get_status()



    def build(self):

        if self.order == None:
            self.page.go("/")
            return None


        return Container(
            content=Column(
                controls=[

                    ## HEADER
                    Container(
                        content=Row(
                            controls=[

                                Row(
                                    controls=[
                                        Row(
                                            controls=[
                                                Container(
                                                    content=IconButton(
                                                        icon=icons.ARROW_BACK_ROUNDED,
                                                        icon_color=ft.colors.PRIMARY,
                                                        icon_size=25,
                                                        on_click=self.back_list_view
                                                    ),
                                                    margin=margin.only(right=10)
                                                ),
                                                Text(value=f'#{self.getOrder.order_number} ' if self.getOrder.order_reference == None else f'#{self.getOrder.order_number} {self.getOrder.order_reference} ', size=20, weight="w700", color=ft.colors.ON_BACKGROUND, selectable=True),
                                                Text(value=f'de {self.getOrder.order_customer}', size=18, weight="w500", color=ft.colors.ON_BACKGROUND, selectable=True),
                                            ],
                                            spacing=0
                                        ),
                                        IconButton(
                                            icon=icons.COPY,
                                            icon_size=20,
                                            data=f'{self.getOrder.order_number if self.getOrder.order_reference == None else self.getOrder.order_reference} - {self.getOrder.order_customer}',
                                            on_click=self.__clipboard
                                        )
                                    ],
                                    vertical_alignment=CrossAxisAlignment.CENTER
                                ),

                                Row(
                                    controls=[
                                        # btn(page=self.page, icon="assignment", text="assinar", style="small", color="primary").outline(),
                                        # btn(page=self.page, icon="print", text="imprimir", style="small", color="primary").outline(),
                                    ]
                                ),

                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        ),
                        bgcolor=ft.colors.BACKGROUND,
                        padding=padding.symmetric(20,30)
                    ),

                    Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.15),

                    # ## FORMULÁRIO PEDIDO

                    Container(
                        content=Column(
                            controls=[

                                ResponsiveRow(
                                    controls=[

                                        ## INFO PEDIDO
                                        Container(
                                            content=Column(
                                                controls=[

                                                    Container(
                                                        content=Column(
                                                            controls=[

                                                                Container(
                                                                    content=Text(value="Detalhes da Venda", size=16, weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY),
                                                                    bgcolor=ft.colors.SECONDARY_CONTAINER,
                                                                    border_radius=border_radius.only(5,5),
                                                                    padding=padding.symmetric(10,20),
                                                                    alignment=alignment.center_left
                                                                ),

                                                                Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                                                Container(
                                                                    content=Column(
                                                                        controls=[

                                                                            ResponsiveRow(
                                                                                controls=[

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.SHOPPING_CART, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Canal de Venda", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=self.getOrder.order_channel,
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.ON_BACKGROUND,
                                                                                                focused_border_color=ft.colors.ON_BACKGROUND,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_channel,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.BUSINESS, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Empresa", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=self.getOrder.order_company,
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_company,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.DATE_RANGE, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Data do Pedido", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=self.getOrder.order_date.strftime('%d/%m/%Y %H:%M:%S'),
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_date,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),

                                                                                ],
                                                                            ),

                                                                            ResponsiveRow(
                                                                                controls=[

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.LOCAL_SHIPPING, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Forma de Envio", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=self.getOrder.order_shippingMethod,
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_shippingMethod,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),                                                        

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.DATE_RANGE, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Data de Envio ATD", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=self.getOrder.order_shippingDate.strftime('%d/%m/%Y %H:%M:%S'),
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_shippingDate,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.DATE_RANGE, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Data de Envio MKP", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),

                                                                                            TextField(
                                                                                                value=self.getOrder.order_shippingDateMKP.strftime('%d/%m/%Y %H:%M:%S') if self.getOrder.order_shippingDateMKP != None else "SEM INTEGRAÇÃO",
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),

                                                                                ],
                                                                            ),

                                                                            Container(height=5),

                                                                            Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                                                            ResponsiveRow(
                                                                                controls=[

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.HEADSET_MIC, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Atendente", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=self.getOrder.order_userSystem,
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_user,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),                                                            

                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.DATE_RANGE, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Data de Importação", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=self.getOrder.order_dateImport.strftime('%d/%m/%Y %H:%M:%S'),
                                                                                                text_style=TextStyle(size=16, weight="w400"),
                                                                                                color=ft.colors.ON_PRIMARY_CONTAINER,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                border=ft.InputBorder.NONE,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                height=35,
                                                                                                dense=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),

                                                                                    Column(
                                                                                        controls=[

                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.PLAYLIST_ADD_CIRCLE_ROUNDED, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Status do Pedido", size=13, weight="w600", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),

                                                                                            Container(
                                                                                                content=Dropdown(
                                                                                                    value=self.getOrder.order_status,
                                                                                                    text_style=TextStyle(size=13, weight="w600"),
                                                                                                    color=ft.colors.ON_BACKGROUND,
                                                                                                    bgcolor=self.__get_bgcolor(self.getOrder.order_status),
                                                                                                    border_color=ft.colors.BACKGROUND,
                                                                                                    border_radius=7,
                                                                                                    focused_color=ft.colors.ON_BACKGROUND,
                                                                                                    content_padding=padding.symmetric(vertical=3, horizontal=10),
                                                                                                    options=self.status_opt,
                                                                                                    filled=True,
                                                                                                    on_change=self.change_status,
                                                                                                    height=40,
                                                                                                    width=210,
                                                                                                    dense=True,
                                                                                                ),
                                                                                                padding=padding.symmetric(vertical=0, horizontal=2),
                                                                                                border_radius=border_radius.all(10)
                                                                                            ),

                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),

                                                                                ],
                                                                            ),

                                                                            Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                                                            Container(height=5),

                                                                            ResponsiveRow(
                                                                                controls=[

                                                                                    Container(
                                                                                        content=Column(
                                                                                            controls=[

                                                                                                Container(
                                                                                                    content=Row(
                                                                                                        controls=[
                                                                                                            Icon(name=icons.PERSON, size=12, color=ft.colors.ON_PRIMARY_CONTAINER),
                                                                                                            Text(value="Comprador", size=15, weight="w600", color=ft.colors.ON_PRIMARY_CONTAINER)
                                                                                                        ],
                                                                                                        spacing=5
                                                                                                    ),
                                                                                                    bgcolor=ft.colors.with_opacity(0.7, ft.colors.SURFACE_VARIANT),
                                                                                                    border_radius=border_radius.all(5),
                                                                                                    padding=padding.symmetric(7,10),
                                                                                                    alignment=alignment.center_left,
                                                                                                    margin=margin.symmetric(5)
                                                                                                ),

                                                                                                TextField(
                                                                                                    value=self.getOrder.order_customer,
                                                                                                    prefix_icon=icons.PERM_IDENTITY,
                                                                                                    tooltip=" Nome do Comprador ",
                                                                                                    text_style=TextStyle(size=14, weight="w400"),
                                                                                                    color=ft.colors.ON_BACKGROUND,
                                                                                                    bgcolor=ft.colors.BACKGROUND,
                                                                                                    border_color=ft.colors.OUTLINE,
                                                                                                    border_radius=5,
                                                                                                    border=ft.InputBorder.NONE,
                                                                                                    focused_color=ft.colors.PRIMARY,
                                                                                                    focused_border_color=ft.colors.PRIMARY,
                                                                                                    content_padding=padding.symmetric(vertical=10, horizontal=10),
                                                                                                    # height=35,
                                                                                                    multiline=True,
                                                                                                    ref=self.order_customer,
                                                                                                    dense=True,
                                                                                                    disabled=True
                                                                                                ),

                                                                                                TextField(
                                                                                                    value=self.getOrder.order_customerNickname if self.getOrder.order_customerNickname != None else None,
                                                                                                    tooltip=" Apelido do Comprador ",
                                                                                                    prefix_icon=icons.PERSON_PIN_OUTLINED if self.getOrder.order_customerNickname != None else None,
                                                                                                    text_style=TextStyle(size=14, weight="w400"),
                                                                                                    color=ft.colors.ON_BACKGROUND,
                                                                                                    bgcolor=ft.colors.BACKGROUND,
                                                                                                    border_color=ft.colors.OUTLINE,
                                                                                                    border_radius=5,
                                                                                                    border=ft.InputBorder.NONE,
                                                                                                    focused_color=ft.colors.PRIMARY,
                                                                                                    focused_border_color=ft.colors.PRIMARY,
                                                                                                    content_padding=padding.symmetric(vertical=5, horizontal=10),
                                                                                                    # height=35,
                                                                                                    multiline=True,
                                                                                                    ref=self.order_customerNickname,
                                                                                                    dense=True,
                                                                                                    disabled=True
                                                                                                ),

                                                                                                TextField(
                                                                                                    value=self.getOrder.order_customerPhone if self.getOrder.order_customerPhone != None else None,
                                                                                                    tooltip=" Telefone do Comprador ",
                                                                                                    prefix_icon=icons.PHONE if self.getOrder.order_customerPhone != None else None,
                                                                                                    text_style=TextStyle(size=14, weight="w400"),
                                                                                                    color=ft.colors.ON_BACKGROUND,
                                                                                                    bgcolor=ft.colors.BACKGROUND,
                                                                                                    border_color=ft.colors.OUTLINE,
                                                                                                    border_radius=5,
                                                                                                    border=ft.InputBorder.NONE,
                                                                                                    focused_color=ft.colors.PRIMARY,
                                                                                                    focused_border_color=ft.colors.PRIMARY,
                                                                                                    content_padding=padding.symmetric(vertical=5, horizontal=10),
                                                                                                    # height=35,
                                                                                                    multiline=True,
                                                                                                    dense=True,
                                                                                                    disabled=True
                                                                                                ),

                                                                                                # TextField(
                                                                                                #     value=self.getOrder.order_customerEmail if self.getOrder.order_customerEmail != None else None,
                                                                                                #     tooltip=" E-mail do Comprador ",
                                                                                                #     prefix_icon=icons.EMAIL if self.getOrder.order_customerEmail != None else None,
                                                                                                #     text_style=TextStyle(size=14, weight="w400"),
                                                                                                #     color=ft.colors.ON_BACKGROUND,
                                                                                                #     bgcolor=ft.colors.BACKGROUND,
                                                                                                #     border_color=ft.colors.OUTLINE,
                                                                                                #     border_radius=5,
                                                                                                #     border=ft.InputBorder.NONE,
                                                                                                #     focused_color=ft.colors.PRIMARY,
                                                                                                #     focused_border_color=ft.colors.PRIMARY,
                                                                                                #     content_padding=padding.symmetric(vertical=5, horizontal=10),
                                                                                                #     # height=35,
                                                                                                #     multiline=True,
                                                                                                #     dense=True,
                                                                                                #     disabled=True
                                                                                                # ),

                                                                                            ],
                                                                                            spacing=0,
                                                                                        ),
                                                                                        col=5
                                                                                    ),

                                                                                    Container(
                                                                                        content=Column(
                                                                                            controls=[

                                                                                                Container(
                                                                                                    content=Row(
                                                                                                        controls=[
                                                                                                            Icon(name=icons.LOCATION_ON, size=12, color=ft.colors.ON_PRIMARY_CONTAINER),
                                                                                                            Text(value="Endereço de Envio", size=15, weight="w600", color=ft.colors.ON_PRIMARY_CONTAINER)
                                                                                                        ],
                                                                                                        spacing=5
                                                                                                    ),
                                                                                                    bgcolor=ft.colors.with_opacity(0.7, ft.colors.SURFACE_VARIANT),
                                                                                                    border_radius=border_radius.all(5),
                                                                                                    padding=padding.symmetric(7,10),
                                                                                                    alignment=alignment.center_left,
                                                                                                    margin=margin.symmetric(5)
                                                                                                ),

                                                                                                TextField(
                                                                                                    value=self.getOrder.order_shippingAddress["enderecoCompleto"],
                                                                                                    text_style=TextStyle(size=14, weight="w400"),
                                                                                                    color=ft.colors.ON_BACKGROUND,
                                                                                                    bgcolor=ft.colors.BACKGROUND,
                                                                                                    border_color=ft.colors.OUTLINE,
                                                                                                    border_radius=5,
                                                                                                    border=ft.InputBorder.NONE,
                                                                                                    focused_color=ft.colors.PRIMARY,
                                                                                                    focused_border_color=ft.colors.PRIMARY,
                                                                                                    content_padding=padding.symmetric(vertical=0, horizontal=10),
                                                                                                    ref=self.order_shippingAddress,
                                                                                                    # height=135,
                                                                                                    dense=True,
                                                                                                    disabled=True,
                                                                                                    multiline=True,
                                                                                                ),

                                                                                            ]
                                                                                        ),
                                                                                        col=7
                                                                                    ),

                                                                                ],
                                                                            ),

                                                                            # Container(height=10)

                                                                        ],
                                                                    ),
                                                                    padding=padding.symmetric(5,10),
                                                                    margin=margin.symmetric(10,7)
                                                                ),

                                                            ],
                                                            spacing=0
                                                        ),
                                                        bgcolor=ft.colors.BACKGROUND,
                                                        padding=padding.symmetric(2,2),
                                                        border_radius=7,
                                                    ),

                                                    Container(
                                                        content=Column(
                                                            controls=[
                                                                Container(
                                                                    content=Column(
                                                                        controls=[
                                                                            ft.Tabs(
                                                                                selected_index=0,
                                                                                tabs=[

                                                                                    ft.Tab(
                                                                                        tab_content=Row(
                                                                                            controls=[
                                                                                                Icon(name=icons.COMMENT_OUTLINED, color=ft.colors.PRIMARY, size=16),
                                                                                                Text(value="Comentários", color=ft.colors.PRIMARY, size=16, weight="w600")
                                                                                            ],
                                                                                            vertical_alignment=CrossAxisAlignment.CENTER
                                                                                        )
                                                                                    ),

                                                                                    ft.Tab(
                                                                                        tab_content=Row(
                                                                                            controls=[
                                                                                                Icon(name=icons.LOCAL_SHIPPING, color=ft.colors.PRIMARY, size=16),
                                                                                                Text(value="Rastreamento", color=ft.colors.PRIMARY, size=16, weight="w600")
                                                                                            ],
                                                                                            vertical_alignment=CrossAxisAlignment.CENTER
                                                                                        )
                                                                                    ),

                                                                                    ft.Tab(
                                                                                        tab_content=Row(
                                                                                            controls=[
                                                                                                Icon(name=icons.TASK_ALT_ROUNDED, color=ft.colors.PRIMARY, size=16),
                                                                                                Text(value="Asana", color=ft.colors.PRIMARY, size=16, weight="w600")
                                                                                            ],
                                                                                            vertical_alignment=CrossAxisAlignment.CENTER
                                                                                        )
                                                                                    ),

                                                                                    ft.Tab(
                                                                                        tab_content=Row(
                                                                                            controls=[
                                                                                                Icon(name=icons.TASK_ALT_ROUNDED, color=ft.colors.PRIMARY, size=16),
                                                                                                Text(value="Magis5", color=ft.colors.PRIMARY, size=16, weight="w600")
                                                                                            ],
                                                                                            vertical_alignment=CrossAxisAlignment.CENTER
                                                                                        )
                                                                                    ),

                                                                                ],
                                                                                on_change=self.change_tabs
                                                                            ),
                                                                        ],
                                                                    ),
                                                                    padding=padding.symmetric(15,15)
                                                                ),

                                                                Container(
                                                                    ref=self.tabs_box,
                                                                    content=self.__tab_comment(),
                                                                    padding=padding.symmetric(10,15)
                                                                )
                                                            ],
                                                            spacing=0
                                                        ),
                                                        bgcolor=ft.colors.BACKGROUND,
                                                        padding=padding.symmetric(2,2),
                                                        border_radius=7,
                                                    ),

                                                ],
                                                spacing=15
                                            ),
                                            margin=margin.symmetric(15,15),
                                            col=7
                                        ),

                                        ## PRODUTO
                                        Container(
                                            content=Column(
                                                controls=[

                                                    Container(
                                                        content=Column(
                                                            controls=[
                                                                Container(
                                                                    content=Text(value="Produtos", size=16, weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY),
                                                                    bgcolor=ft.colors.SECONDARY_CONTAINER,
                                                                    border_radius=border_radius.only(5,5),
                                                                    padding=padding.symmetric(10,20),
                                                                    alignment=alignment.center_left
                                                                ),

                                                                Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                                                Container(
                                                                    content=Column(controls=self.lista_produtos, alignment=MainAxisAlignment.SPACE_EVENLY),
                                                                    margin=margin.only(15,15,15,5)
                                                                )
                                                            ],
                                                            spacing=0
                                                        ),
                                                        bgcolor=ft.colors.BACKGROUND,
                                                        padding=padding.symmetric(2,2),
                                                        border_radius=7,
                                                        col=5
                                                    )

                                                ],
                                                spacing=15
                                            ),
                                            margin=margin.symmetric(15,15),
                                            col=5
                                        ),

                                    ],                                    
                                    vertical_alignment=CrossAxisAlignment.START,
                                    spacing=0
                                ),
                            
                            ],
                            scroll=ft.ScrollMode.ALWAYS
                        ),
                        expand=True
                    ),

                ],
                spacing=0,
            ),
            alignment=alignment.top_center,
        )



    ## FUNÇÕES DE CONTEÚDO  ------

    def get_order(self, id):

        """ Função para obter os dados do pedido """

        self.getOrder = ORDER_REP().filter_id(id)
        self.getProduct = ORDER_PRD().filter_number(self.getOrder.order_number)
        print(f'\n👁 VISUALIZAÇÃO DE PEDIDO = #{self.getOrder.order_number}, por {self.user_system["name"]} em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')

        index_product = 1
        self.lista_produtos = list()
        for product in self.getProduct:
            self.lista_produtos.append(
                Container(
                    content=Column(
                        controls=[
                            ft.ListTile(
                                leading=Container(
                                    content=ft.Image(src=product.icon, fit=ImageFit.FILL, border_radius=border_radius.all(100), error_content=Image(src="V4/assets/images/system/nopreview.png", fit=ImageFit.FILL, border_radius=border_radius.all(100))),
                                    data={"index": index_product, "img": product.icon},
                                    padding=padding.all(0),
                                    margin=margin.all(0),
                                    height=80,
                                    width=60
                                ),
                                title=Text(value=f'{product.name}'.upper(), size=14, weight=ft.FontWeight.W_700, color=ft.colors.PRIMARY),
                                subtitle=Column(
                                    controls=[
                                        Row(
                                            controls=[
                                                Text(value="SKU:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                                Text(value=product.sku, size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                            ]
                                        ),
                                        Row(
                                            controls=[
                                                Text(value="QUANTIDADE:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                                Text(value=f"{product.qty} UND" if product.qty == 1 else f"{product.qty} UNDS", size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                            ]
                                        ),
                                    ],
                                    spacing=1
                                ),
                                content_padding=padding.symmetric(horizontal=0),
                            ),
 
                            TextField(
                                value=product.customization,
                                label="Personalização",
                                label_style=TextStyle(size=16, weight="w600"),
                                text_style=TextStyle(size=16, weight="w600"),
                                color=ft.colors.ON_BACKGROUND,
                                bgcolor=ft.colors.BACKGROUND,
                                border_color=ft.colors.SECONDARY_CONTAINER,
                                border_radius=5,
                                focused_color=ft.colors.PRIMARY,
                                focused_border_color=ft.colors.PRIMARY,
                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                height=40,
                                data=index_product,
                                disabled=True
                            ),
                        ],
                        spacing=15
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=5,
                    padding=padding.symmetric(15,15),
                    margin=margin.only(bottom=10),
                    col=12
                )
            )

            index_product+=1

        self.update()
        self.page.update()


    def __tab_comment(self):

        return NotesTemplate(
            page = self.page,
            set_module = "order",
            set_reference = self.getOrder.order_number,
            set_user= self.user_system["name"],
            task_ids= self.getOrder.order_task,
            set_systemnote = self.getOrder.order_historic
        ).create_template()


    def __tab_shippiment(self):

        return TrackingTemplate(
            page = self.page,
            gateway = str(self.getOrder.order_channel).replace(" ", "").lower(),
            company = self.getOrder.order_company,
            order_number = self.getOrder.order_number,
            track_number = self.getOrder.order_shippingTracking
        ).create_template()


    def __tab_asana(self, delete:bool=False):

        task_gids = self.getOrder.order_task if self.asana_task_create == None else {"gid": self.asana_task_create}

        return AsanaTemplate(
            page = self.page,
            task = task_gids if not delete else {"gid": []},
            event_create = self.pre_task,
            event_delete=self.delete_task
        ).create_template()


    def __tab_magis5(self):
        """ Busca informações do pedido no Magis5 HUB. """

        match self.getOrder.order_channel:

            case "TikTok":
                order_number = f'{self.getOrder.order_number}-{self.getOrder.order_shippingTracking}'
            case "Prestashop":
                order_number = self.getOrder.order_reference
            case _:
                order_number = self.getOrder.order_number

        return Magis5Template(order_id=order_number).create_template()


    def change_tabs(self, e):

        if self.tabs_box.current.content != None:
            self.tabs_box.current.clean()
            self.tabs_box.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
            self.tabs_box.current.update()

        match e.control.selected_index:

            case 0:
                self.tabs_box.current.content = self.__tab_comment()
                self.tabs_box.current.update()
                self.page.update()

            case 1:
                self.tabs_box.current.content = self.__tab_shippiment()
                self.tabs_box.current.update()
                self.page.update()

            case 2:
                self.tabs_box.current.content = self.__tab_asana()
                self.tabs_box.current.update()
                self.page.update()

            case 3:
                self.tabs_box.current.content = self.__tab_magis5()
                self.tabs_box.current.update()
                self.page.update()                

    ## ------


    def pre_task(self, e):

        """ Verifica a quantidade de produtos no pedido para verificar a necessidade de criar uma ou mais tarefas do mesmo pedido (partição). """

        try:
            if len(self.getProduct) > 1:
                self.alert.info_dialog(
                    text="Pedido com mais de um produto.\nDeseja dividir em mais de uma tarefa?",
                    act=[
                        btn(page=self.page, text="Sim", color="primary", style="small", event=self.task_divider),
                        btn(page=self.page, text="Não", color="warning", style="small", event=self.save_task)
                    ]
                )
                self.page.dialog = self.alert
                self.alert.open = True
                self.page.update()
                return None

            else:
                print(f'\n▶️  NOVO ENVIO DE PEDIDO P/ ASANA = #{self.getOrder.order_number}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
                self.save_task(None)

        except Exception as exc:
            print(f'\n❌ ORDER_VIEW > pre_task() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()
            return None


    def task_divider(self, e):

        print(f'\n▶️  NOVO ENVIO DE PEDIDO P/ ASANA = #{self.getOrder.order_number}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')

        self.index_product = 0
        self.partitions = 0
        self.divider_list = list()

        def add_partition(e):
            self.partitions +=1
            if self.partitions > 3:
                self.snackbar.warning(msg="Limite máximo de partições atingido.")
                self.page.update()
                return None
            self.product_divider.current.columns.append(ft.DataColumn(Text(f'PARTE {self.partitions}', color=ft.colors.BACKGROUND)))
            for indice, linha in enumerate(self.product_divider.current.rows):
                linha.cells.append(
                    ft.DataCell(
                        ft.Checkbox(
                            check_color=ft.colors.BACKGROUND,
                            fill_color={"selected": ft.colors.LIGHT_GREEN_700},
                            data={"index": indice, "partition": self.partitions},
                            on_change=selected
                        )
                    )
                )

            self.page.update() 

        def selected(e):
            if e.control.value == True:
                self.divider_list.append({"product": e.control.data, "check": e.control.value})
            else:
                for product in self.divider_list:
                    if product["product"]["index"] == e.control.data["index"] and product["product"]["partition"] == e.control.data["partition"]:
                        self.divider_list.remove(product)

        self.view = Column(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            ft.DataTable(
                                width=2600,
                                column_spacing=50,
                                vertical_lines=ft.BorderSide(1, ft.colors.OUTLINE),
                                data_row_color={"hovered": ft.colors.SECONDARY_CONTAINER},
                                heading_row_color= ft.colors.SECONDARY,
                                heading_row_height=35,
                                show_bottom_border=True,
                                columns=[ft.DataColumn(Text("Produto", color=ft.colors.BACKGROUND))],
                                ref=self.product_divider
                            )
                        ],
                    ),
                    margin=margin.symmetric(horizontal=15),
                    padding=padding.symmetric(vertical=15)
                ),
            ],
            alignment=MainAxisAlignment.START,
            width=600,
            height=340,
            scroll="auto"
        )

        for product in self.getProduct:
            self.product_divider.current.rows.append(ft.DataRow(cells=[ft.DataCell(Text(f'{product.name} ({product.customization})'))]))

        self.alert.close_dialog()
        self.update()

        self.alert.default_dialog(
            contt=self.view,
            act=[
                btn(page=self.page, text="salvar", style="small", color="primary", event=self.task_saveDivider),
                btn(page=self.page, text="fechar", style="small", color="danger", event=self.close_dialog),
            ],
            title= Container(
                content=Column(
                    controls=[
                        Row(
                            controls=[
                                Row(
                                    controls=[
                                        Icon(icons.ADD_TASK_OUTLINED, color=ft.colors.ON_BACKGROUND, size=22),
                                        Text(value="Dividir Pedido Em Tarefas", size=17, weight="w600", color=ft.colors.ON_BACKGROUND),
                                    ]
                                ),
                                ft.FloatingActionButton(
                                    text="PARTIÇÃO",
                                    icon=icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                                    bgcolor=ft.colors.PRIMARY if self.page.theme_mode == "dark" else ft.colors.PRIMARY_CONTAINER,
                                    on_click=add_partition,
                                    mini=True
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        ),
                        Divider(height=0.5, color=ft.colors.OUTLINE, visible=True),
                    ],
                ),
               margin=margin.symmetric(horizontal=15)
            ),
        ),

        self.page.dialog = self.alert
        self.alert.open = True
        self.page.update()


    def task_saveDivider(self, e):

        if self.partitions <= 1:
            self.snackbar.warning(msg="Erro, adicione pelo menos duas partições para continar.")
            self.page.update()
            return

        if len(self.divider_list) < len(self.getProduct):
            self.snackbar.warning(msg="Erro, marque todos os produtos em uma partição para continar.")
            self.page.update()
            return None

        product_partition = []
        product_index = []

        for product in self.divider_list:
            product_partition.append(product["product"]["partition"])
            product_index.append(product["product"]["index"])

        duplicate = [x for x in product_index if product_index.count(x) > 1]

        if len(duplicate) > 0:
            self.snackbar.warning(msg="Erro, produto(s) marcado em mais de uma partição. Marque cada produto em APENAS uma partição para continuar.")
            self.page.update()
            product_partition.clear()
            product_index.clear()
            return None

        if len(set(product_partition)) != self.partitions:
            self.snackbar.warning(msg="Erro, não pode haver partições vazias. Marque pelo menos um produto para cada partição.")
            self.page.update()
            product_partition.clear()
            product_index.clear()
            return None

        self.alert.close_dialog()
        self.alert.progress_dialog("Enviado Pedido P/ Asana")
        self.page.dialog = self.alert
        self.alert.open = True
        self.page.update()

        try:
            self.asana_gid = list()
            self.copy_products = list()

            for part in range(int(self.partitions)):
                for product in self.divider_list:
                    if product["product"]["partition"] == (part+1):
                        index = product["product"]["index"]
                        self.copy_products.append(self.getProduct[index])

                task = self.__save_task(partition=[part+1, self.partitions]) ##SAVE_TASK
                self.asana_gid.append(task["data"]["gid"])
                self.copy_products.clear()

            self.asana_task_create = self.asana_gid
            ORDER_REP().update(id=self.getOrder.id, fild="order_task", data={"gid": self.asana_gid})
            print(f'\n🧾 PEDIDO ENVIADO P/ ASANA = #{self.getOrder.order_number}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')

            self.tabs_box.current.content.clean()
            self.tabs_box.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
            self.tabs_box.current.update()

            self.tabs_box.current.content = self.__tab_asana()
            self.tabs_box.current.update()

            self.alert.open = False
            self.page.update()
            self.clear_uploads()

        except Exception as ex:
            print(f'\n❌ ORDER_VIEW > TASK_SAVEDIVIDER() ==> EXCEPTION: ==> {ex}\n')
            self.snackbar.internal_error()
            self.alert.open = False
            self.page.update()
            self.clear_uploads()


    def save_task(self, e):

        self.alert.close_dialog()
        self.alert.progress_dialog("Enviado Pedido P/ Asana")
        self.page.dialog = self.alert
        self.alert.open = True
        self.page.update()

        try:
            task = self.__save_task() ## SAVE_TASK
            self.asana_task_create = [task["data"]["gid"]]
            ORDER_REP().update(id=self.getOrder.id, fild="order_task", data={"gid": self.asana_task_create})
            print(f'\n🧾 PEDIDO ENVIADO P/ ASANA = #{self.getOrder.order_number}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')

            self.tabs_box.current.content.clean()
            self.tabs_box.current.content = Container(content=ft.ProgressRing(), alignment=alignment.center)
            self.tabs_box.current.update()

            self.tabs_box.current.content = self.__tab_asana()
            self.tabs_box.current.update()
            self.page.update()

            self.alert.open = False
            self.page.update()
            self.clear_uploads()

        except Exception as ex:
            print(f'\n❌ ORDER_VIEW > SAVE_TASK() ==> EXCEPTION: {ex}\n')
            self.snackbar.internal_error()
            self.alert.open = False
            self.page.update()
            self.clear_uploads()


    def __save_task(self, partition:list=None):

        try:
            company = COMPANY().filter_name(self.getOrder.order_company)
            search_carrier = CARRIER().filter_name(self.getOrder.order_shippingMethod)
            attendant = USER().filter_name(self.getOrder.order_userSystem)

            search_channel = SALES().filter_all()
            for chn in search_channel:
                if chn.name == self.getOrder.order_channel and chn.company["name"] == self.getOrder.order_company:
                    channel = {"id": chn.asanaID, "name": chn.name}

            list_products = self.getProduct if partition == None else self.copy_products

            data = {
                "completion_date": self.getOrder.order_shippingDate,
                "project": "arte_final",
                "custom_fields": {
                    "channel": channel["id"],
                    "company": company.asanaID,
                    "attendant": attendant.asanaID,
                    "shippingMethod": search_carrier.asanaID
                },
                "info": {
                    "number": self.getOrder.order_number if self.getOrder.order_reference == None else f'{self.getOrder.order_number} ({self.getOrder.order_reference})',
                    "customer": self.getOrder.order_customer,
                    "date": self.order_date.current.value,
                    "channel": channel["name"],
                    "company": company.name,
                    "attendant": attendant.name,
                    "address": self.order_shippingAddress.current.value,
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
                "comments": [{"text": self.getOrder.order_historic, "pinned" : False}]
            }

            if partition != None:
                create = TASK().create(type_body="order", task_data=data, partition=f'[Parte {partition[0]}/{partition[1]}]')
            else:
                create = TASK().create(type_body="order", task_data=data)

            return create


        except Exception as exc:
            print(f'\n❌ ORDER_VIEW > __save_task() ==> EXCEPTION: {exc}\n')
            self.alert.open = False
            self.page.update()
            self.clear_uploads()



    ## OUTRAS FUNÇÕES ------

    def clear_uploads(self):
        """ Limpa o diretório de uploads quando for anexado imagem ou documentos nos comentários. """

        try:
            path_dir = f'V4/upload/{self.getOrder.order_number}'
            if os.path.isdir(path_dir):
                shutil.rmtree(path=path_dir, ignore_errors=True)

        except Exception as exc:
            print(f'\n❌ ORDER_VIEW > clear_uploads() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def __clipboard(self, e):

        """ Função para copiar dados para a área de transferência """

        try:
            self.page.set_clipboard(e.control.data)
            self.snackbar.clipboard()
            self.page.update()

        except Exception as exc:
            print(f'\n❌ ORDER_VIEW > __clipboard() ==> EXCEPTION: {exc}\n')


    def back_list_view(self, e):

        """ Retorna para a listagem de pedido. """
        try:
            self.page.go("/pedidos")

        except Exception as exc:
            print(f'\n❌ ORDER_VIEW > back_list_view() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def __get_status(self):

        """ Obtem opções de status do pedido. """

        self.status_list = list()
        self.status_opt = list()
        self.status_color = dict()

        get_status = STATUS().filter_module("order")

        for status in get_status:
            self.status_list.append(status.name)
            self.status_color[status.name] = status.color

        self.status_list.sort()
        for sts in self.status_list:
            self.status_opt.append(dropdown.Option(sts, disabled=False if sts != "Importado" else True))

        return self.status_opt


    def __get_bgcolor(self, color):
        """ Obtem a cor do status. """
        return self.status_color[color]


    def change_status(self, e):

        try:
            ORDER_REP().update(id=self.getOrder.id, fild="order_status", data=e.control.value)
            self.snackbar.sucess(msg="Status do pedido atualizado com sucesso")
            e.control.bgcolor = self.status_color[e.control.value]
            self.update()
            self.page.update()

        except Exception as exc:
            print(f'ORDER_VIEW - change_status() ==> {exc}')

    ## ------



    def delete_task(self, e):
        """ Delete uma tarefa do banco de dados e do Asana. """

        try:
            if self.user_system["user"] in ['admin@fadrixsys', 'celio@fadrixsys', 'andrei@fadrixsys']:

                self.alert.progress_dialog("Deletando Tarefa No Asana")
                self.page.dialog = self.alert
                self.alert.open = True
                self.page.update()

                task = self.getOrder.order_task
                task_gid = list()

                ORDER_REP().update(id=self.getOrder.id, fild="order_task", data={"gid": []})

                for key, value in task.items():
                    match isinstance(value, str):
                        case True:
                            task_gid.append(value)
                        case False:
                            for gid in value:
                                task_gid.append(gid)

                for value_gid in task_gid:
                    AsanaAPI().delete_a_task(task_gid=value_gid)

                    NOTE().insert(
                        sign = null(),
                        module = "order",
                        reference = self.getOrder.order_number,
                        user = self.user_system["name"],
                        date = datetime.now(),
                        type_msg = "text",
                        text = f'Tarefa Asana #{value_gid}, deletada com sucesso!',
                        sticker = null(),
                        image = null(),
                        audio = null(),
                        video = null(),
                        attachment = null(),
                        reply = null()
                    )                    

                self.tabs_box.current.content = self.__tab_asana(delete=True)
                self.tabs_box.current.update()
                self.page.update()
                self.getOrder.order_task = {"gid": []}

                self.alert.open = False
                self.snackbar.sucess(msg="Tarefa no Asana deletada com sucesso.")
                self.page.update()

            else:
                self.snackbar.warning(msg="Permissão negada para essa ação.")
                self.page.update()


        except Exception as exc:
            print(f'\n❌ ASANAGET > delete_task == EXCEPTION: {exc}\n')
            self.alert.open = False
            self.snackbar.internal_error()
            self.page.update()
            return None

import os, shutil
import flet as ft
from flet import (
    Page, UserControl, Ref,
    Column, Row, ResponsiveRow, Container, Divider,
    DataTable, DataColumn, DataRow, DataCell,
    Text, TextStyle, TextField, Dropdown, Checkbox, IconButton, FloatingActionButton, Image, ImageFit,
    Icon, MainAxisAlignment, CrossAxisAlignment, BorderSide,
    dropdown, icons, margin, padding, alignment, border_radius
)

from datetime import datetime

## Conexão com Dados
from data.repository.company import CompanyRepository as COMPANY
from data.repository.orderV2 import OrderRepositoryV2 as ORDER_REP
from data.repository.order_product import OrderProductRepository as ORDER_PRD
from data.repository.commentsV2 import CommentsV2Repository as NOTE
from data.repository.company import CompanyRepository as COMPNY
from source.api.prestashopApi import Prestashop as PS
from sqlalchemy import null

## Controles do Sistema
from controllers.date_control import date_create as DATE
from controllers.order_control import OrderControl as ORDER
from controllers.task_control import TaskControl as TASK

## COMPONENTES TEMPLATE
from view.component.buttons import ButtonsComponents as btn
from view.component.dialog import Dialog
from view.component.snackbar import SnackBar_PATTERNS

## WIDGET TEMPLATE
from view.widget.calendar import Calendar


class OrderImport(UserControl):

    def __init__(self, page: Page):
        super().__init__()
        self.page = page

        # INFORMAÇÕES DE SESSÃO:
        self.user_system = self.page.client_storage.get("user_info")
        self.app_config = self.page.session.get("app_config")
        ## ---------

        ## WIDGETS:
        self.alert = Dialog(self.page)
        self.snackbar = SnackBar_PATTERNS(self.page)
        self.calend = Calendar(self.page, self.select_date)
        ## ---------

        ## VARIÁVEIS (REFs):
        self.__order_response = None
        self.__orderProduct_response = None
        self.order_commentSystem = None

        self.logo_channel = Ref[Image]()
        self.order_number = Ref[Text]()
        self.order_channel = Ref[TextField]()
        self.order_company = Ref[TextField]()
        self.order_date = Ref[TextField]()
        self.order_shippingMethod = Ref[TextField]()
        self.order_shippingDate = Ref[TextField]()
        self.order_customer = Ref[TextField]()
        self.order_customerNickname = Ref[TextField]()
        self.order_shippingAddress = Ref[TextField]()
        self.order_commentUser = Ref[TextField]()
        self.userComment_pinned = Ref[Checkbox]()
        self.text_attachment = Ref[TextField]()
        self.attachment_asana = Ref[Checkbox]()
        self.button_attachment = Ref[ft.ElevatedButton]()

        self.order_getNumber = Ref[TextField]()
        self.order_getHub = Ref[Dropdown]()
        self.order_getCart = Ref[Dropdown]()
        self.order_ColumnCart = Ref[Column]()
        self.order_getShop = Ref[Dropdown]()
        self.order_ColumnShop = Ref[Column]()
        self.order_getCompany = Ref[Dropdown]()
        self.order_ColumnCompany = Ref[Column]()

        self.column_product = Ref[Column]()
        self.img_product = Ref[Image]()
        self.container_img_product = Ref[Container]()

        self.product_divider = Ref[DataTable]()
        self.task_ID = dict()
        ## ---------

        self.attachment_file = ft.FilePicker(on_result=self.attachment_result, on_upload=self.attachment_progress)
        self.page.overlay.append(self.attachment_file)

        self.product_image = ft.FilePicker(on_result=self.product_image_result, on_upload=self.product_image_progress)
        self.page.overlay.append(self.product_image)



    def build(self):

        self.page.floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD)
        self.page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

        get_company = COMPNY().filter_all()
        list_companys = list()
        for cpny in get_company:
            list_companys.append(dropdown.Option(key=cpny.name, text=f"Fadrix {str(cpny.name).split(" ")[0]}"))

        return Container(
            content=Column(
                controls=[

                    ## HEADER
                    Container( 
                        content=Row(
                            controls=[
                                Row(
                                    controls=[
                                        Column(
                                            controls=[
                                                Row(
                                                    controls=[
                                                        Icon(name=icons.NUMBERS, size=12, color=ft.colors.ON_BACKGROUND),
                                                        Text(value="Número Pedido", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                                    ],
                                                    spacing=3
                                                ),
                                                TextField(
                                                    value=None,
                                                    text_style=TextStyle(size=16, weight="w600"),
                                                    color=ft.colors.ON_BACKGROUND,
                                                    bgcolor=ft.colors.BACKGROUND,
                                                    border_color=ft.colors.OUTLINE,
                                                    border_radius=5,
                                                    focused_color=ft.colors.PRIMARY,
                                                    focused_border_color=ft.colors.PRIMARY,
                                                    content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                    width=250,
                                                    height=35,
                                                    ref=self.order_getNumber,
                                                ),
                                            ],
                                            spacing=5
                                        ),
                                        Column(
                                            controls=[
                                                Row(
                                                    controls=[
                                                        Icon(name=icons.LIST, size=12, color=ft.colors.ON_BACKGROUND),
                                                        Text(value="Integração", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                                    ],
                                                    spacing=3
                                                ),
                                                Dropdown(
                                                    value="iderisV3",
                                                    text_style=TextStyle(size=16, weight="w600"),
                                                    color=ft.colors.ON_BACKGROUND,
                                                    bgcolor=ft.colors.BACKGROUND,
                                                    border_color=ft.colors.OUTLINE,
                                                    border_radius=5,
                                                    focused_color=ft.colors.PRIMARY,
                                                    focused_border_color=ft.colors.PRIMARY,
                                                    content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                    width=180,
                                                    height=35,
                                                    ref=self.order_getHub,
                                                    options=[
                                                        # dropdown.Option(key="americanas_api", text="Americanas"),
                                                        dropdown.Option(key="magalu_api", text="Magalu"),
                                                        dropdown.Option(key="meli_api", text="Mercado Livre"),
                                                        dropdown.Option(key="prestashop", text="PrestaShop"),
                                                        dropdown.Option(key="shein_api", text="Shein"),
                                                        dropdown.Option(key="shopee_api", text="Shopee"),
                                                        dropdown.Option(key="tiktok_api", text="TikTok Shop"),
                                                        dropdown.Option(key="magis5hub", text="Magis5 HUB"),
                                                        #dropdown.Option(key="iderisV3", text="Hub Ideris"),
                                                        # dropdown.Option(key="tiny", text="Hub Tiny"),
                                                    ],
                                                    filled=True,
                                                    on_change=self.valide_integration
                                                ),
                                            ],
                                            spacing=5
                                        ),
                                        Column(
                                            controls=[
                                                Row(
                                                    controls=[
                                                        Icon(name=icons.SHOPPING_CART, size=12, color=ft.colors.ON_BACKGROUND),
                                                        Text(value="Selecionar Loja", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                                    ],
                                                    spacing=3
                                                ),
                                                Dropdown(
                                                    value=1,
                                                    text_style=TextStyle(size=16, weight="w600"),
                                                    color=ft.colors.ON_BACKGROUND,
                                                    bgcolor=ft.colors.BACKGROUND,
                                                    border_color=ft.colors.OUTLINE,
                                                    border_radius=5,
                                                    focused_color=ft.colors.PRIMARY,
                                                    focused_border_color=ft.colors.PRIMARY,
                                                    content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                    width=150,
                                                    height=35,
                                                    ref=self.order_getShop,
                                                    options=[
                                                        dropdown.Option(key=1, text="Fadrix"),
                                                        dropdown.Option(key=2, text="Revenda"),
                                                    ],
                                                    filled=True,
                                                ),
                                            ],
                                            ref=self.order_ColumnShop,
                                            visible=False,
                                            spacing=5,
                                        ),
                                        Column(
                                            controls=[
                                                Row(
                                                    controls=[
                                                        Icon(name=icons.BUSINESS, size=12, color=ft.colors.ON_BACKGROUND),
                                                        Text(value="Empresa", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                                    ],
                                                    spacing=3
                                                ),
                                                Dropdown(
                                                    value=None,
                                                    text_style=TextStyle(size=16, weight="w600"),
                                                    color=ft.colors.ON_BACKGROUND,
                                                    bgcolor=ft.colors.BACKGROUND,
                                                    border_color=ft.colors.OUTLINE,
                                                    border_radius=5,
                                                    focused_color=ft.colors.PRIMARY,
                                                    focused_border_color=ft.colors.PRIMARY,
                                                    content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                    width=150,
                                                    height=35,
                                                    ref=self.order_getCompany,
                                                    options=list_companys,
                                                    filled=True,
                                                ),
                                            ],
                                            ref=self.order_ColumnCompany,
                                            visible=False,
                                            spacing=5,
                                            col=6
                                        ),
                                        Column(
                                            controls=[
                                                Row(
                                                    controls=[
                                                        Icon(name=icons.SHOPPING_CART, size=12, color=ft.colors.ON_BACKGROUND),
                                                        Text(value="Carrinho MELI", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
                                                    ],
                                                    spacing=3
                                                ),
                                                Dropdown(
                                                    value='0',
                                                    text_style=TextStyle(size=16, weight="w600"),
                                                    color=ft.colors.ON_BACKGROUND,
                                                    bgcolor=ft.colors.BACKGROUND,
                                                    border_color=ft.colors.OUTLINE,
                                                    border_radius=5,
                                                    focused_color=ft.colors.PRIMARY,
                                                    focused_border_color=ft.colors.PRIMARY,
                                                    content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                    width=150,
                                                    height=35,
                                                    ref=self.order_getCart,
                                                    options=[
                                                        dropdown.Option(key='1', text="SIM"),
                                                        dropdown.Option(key='0', text="NÃO"),
                                                    ],
                                                    filled=True,
                                                    disabled=True
                                                ),
                                            ],
                                            ref=self.order_ColumnCart,                       
                                            spacing=5,                                            
                                        ),                                        
                                        ft.IconButton(icon=icons.SEARCH, bgcolor=ft.colors.SECONDARY_CONTAINER, on_click=self.get_order)
                                    ],
                                    vertical_alignment=CrossAxisAlignment.END
                                ),
                                Row(controls=[btn(page=self.page, icon="save", text="salvar", style="small", color="primary", event=self.pre_save)]),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        ),
                        bgcolor=ft.colors.BACKGROUND,
                        padding=padding.symmetric(20,30)
                    ),

                    Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.15),
                    
                    ## FORMULÁRIO PEDIDO
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
                                                                    content=Row(
                                                                        controls=[
                                                                            ft.Image(src="assets/images/system/saleschannel_default.png", border_radius=100, width=30, ref=self.logo_channel),
                                                                            Text(value=None, size=18, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND, ref=self.order_number)
                                                                        ]
                                                                    ),
                                                                    bgcolor=ft.colors.SURFACE_VARIANT,
                                                                    border_radius=border_radius.all(5),
                                                                    padding=padding.symmetric(12,10),
                                                                    margin=margin.symmetric(10,7)
                                                                ),

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
                                                                                                    Text(value="Canal de Venda", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.ON_BACKGROUND,
                                                                                                focused_border_color=ft.colors.ON_BACKGROUND,
                                                                                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_channel,
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
                                                                                                    Text(value="Empresa", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_company,
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
                                                                                                    Text(value="Data do Pedido", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_date,
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
                                                                                                    Text(value="Forma de Envio", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_shippingMethod,
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
                                                                                                    Text(value="Data de Envio", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_shippingDate,
                                                                                                suffix=IconButton(icons.CALENDAR_MONTH, icon_size=18, icon_color=ft.colors.PRIMARY, width=30, height=30, on_click=self.open_calendar),
                                                                                                read_only=True,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=4
                                                                                    ),                                                            

                                                                                ],
                                                                            ),

                                                                            Container(height=15),

                                                                            Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                                                            Container(height=15),

                                                                            ResponsiveRow(
                                                                                controls=[
                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.PERSON, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Cliente", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_customer,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=9
                                                                                    ),
                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.PERSON, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Usuário", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                                                                height=35,
                                                                                                ref=self.order_customerNickname,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=3
                                                                                    ),
                                                                                ],
                                                                            ),

                                                                            ResponsiveRow(
                                                                                controls=[
                                                                                    Column(
                                                                                        controls=[
                                                                                            Row(
                                                                                                controls=[
                                                                                                    Icon(name=icons.LOCATION_ON, size=14, color=ft.colors.ON_BACKGROUND),
                                                                                                    Text(value="Endereço de Envio", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                                                ],
                                                                                                spacing=3
                                                                                            ),
                                                                                            TextField(
                                                                                                value=None,
                                                                                                text_style=TextStyle(size=16, weight="w600"),
                                                                                                color=ft.colors.ON_BACKGROUND,
                                                                                                bgcolor=ft.colors.BACKGROUND,
                                                                                                border_color=ft.colors.OUTLINE,
                                                                                                border_radius=5,
                                                                                                focused_color=ft.colors.PRIMARY,
                                                                                                focused_border_color=ft.colors.PRIMARY,
                                                                                                content_padding=padding.symmetric(vertical=5, horizontal=10),
                                                                                                ref=self.order_shippingAddress,
                                                                                                disabled=True,
                                                                                                multiline=True,
                                                                                                min_lines=3,
                                                                                                max_lines=3
                                                                                            ),
                                                                                        ],
                                                                                        spacing=5,
                                                                                        col=12
                                                                                    ),
                                                                                ],
                                                                            ),

                                                                            Container(height=10)

                                                                        ],
                                                                    ),
                                                                    padding=padding.symmetric(7,10),
                                                                    margin=margin.symmetric(7,7)
                                                                ),

                                                            ],
                                                            spacing=0
                                                        ),
                                                        bgcolor=ft.colors.BACKGROUND,
                                                        padding=padding.symmetric(2,2),
                                                        border_radius=7,
                                                    ),

                                                    ResponsiveRow(
                                                        controls=[

                                                            Container(
                                                                content=Column(
                                                                    controls=[
                                                                        Container(
                                                                            content=Text(value="Anotações", size=16, weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY),
                                                                            bgcolor=ft.colors.SECONDARY_CONTAINER,
                                                                            border_radius=border_radius.only(5,5),
                                                                            padding=padding.symmetric(10,20),
                                                                            alignment=alignment.center_left
                                                                        ),

                                                                        Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                                                        Container(
                                                                            content=Column(
                                                                                controls=[
                                                                                    TextField(
                                                                                        value=None,
                                                                                        text_style=TextStyle(size=16, weight="w600"),
                                                                                        color=ft.colors.ON_BACKGROUND,
                                                                                        bgcolor=ft.colors.BACKGROUND,
                                                                                        border_color=ft.colors.OUTLINE,
                                                                                        border_radius=5,
                                                                                        focused_color=ft.colors.PRIMARY,
                                                                                        focused_border_color=ft.colors.PRIMARY,
                                                                                        multiline=True,
                                                                                        max_lines=3,
                                                                                        min_lines=3,
                                                                                        ref=self.order_commentUser,
                                                                                        disabled=True
                                                                                    ),
                                                                                    Checkbox(
                                                                                        label="Fixar no Asana",
                                                                                        check_color=ft.colors.BACKGROUND,
                                                                                        fill_color={"selected": ft.colors.PRIMARY},
                                                                                        ref=self.userComment_pinned,
                                                                                        disabled=True
                                                                                    ),
                                                                                ],
                                                                                alignment=MainAxisAlignment.SPACE_BETWEEN
                                                                            ),
                                                                            padding=padding.symmetric(15,15)
                                                                        )
                                                                    ],
                                                                    spacing=0
                                                                ),
                                                                bgcolor=ft.colors.BACKGROUND,
                                                                padding=padding.symmetric(2,2),
                                                                border_radius=7,
                                                                height=240,
                                                                col=6
                                                            ),

                                                            Container(
                                                                content=Column(
                                                                    controls=[
                                                                        Container(
                                                                            content=Text(value="Anexos", size=16, weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY),
                                                                            bgcolor=ft.colors.SECONDARY_CONTAINER,
                                                                            border_radius=border_radius.only(5,5),
                                                                            padding=padding.symmetric(10,20),
                                                                            alignment=alignment.center_left
                                                                        ),

                                                                        Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                                                        Container(
                                                                            content=Column(
                                                                                controls=[
                                                                                    TextField(
                                                                                        value=None,
                                                                                        text_style=TextStyle(size=16, weight="w500"),
                                                                                        color=ft.colors.ON_BACKGROUND,
                                                                                        bgcolor=ft.colors.BACKGROUND,
                                                                                        border_color=ft.colors.ON_INVERSE_SURFACE,
                                                                                        border_radius=5,
                                                                                        focused_color=ft.colors.PRIMARY,
                                                                                        focused_border_color=ft.colors.PRIMARY,
                                                                                        multiline=True,
                                                                                        max_lines=3,
                                                                                        min_lines=3,
                                                                                        read_only=True,
                                                                                        ref=self.text_attachment,
                                                                                    ),
                                                                                    Row(
                                                                                        controls=[
                                                                                            ft.ElevatedButton(
                                                                                                text="Escolher",
                                                                                                ref=self.button_attachment,
                                                                                                disabled=True,
                                                                                                on_click=lambda _: self.attachment_file.pick_files(
                                                                                                    dialog_title="Anexar arquivos",
                                                                                                    initial_directory="/Desktop",
                                                                                                    file_type=ft.FilePickerFileType.ANY,
                                                                                                    allowed_extensions=["jpg", "jpeg", "png", "tif", "cdr", "psd", "ai", "pdf"],
                                                                                                    allow_multiple=True,
                                                                                                )
                                                                                            ),
                                                                                            Checkbox(
                                                                                                label="Anexar no Asana",
                                                                                                check_color=ft.colors.BACKGROUND,
                                                                                                fill_color={"selected": ft.colors.PRIMARY},
                                                                                                ref=self.attachment_asana,
                                                                                                disabled=True
                                                                                            ),
                                                                                        ],
                                                                                        alignment=MainAxisAlignment.SPACE_BETWEEN
                                                                                    )
                                                                                ],
                                                                                spacing=10,
                                                                            ),
                                                                            padding=padding.symmetric(15,15)
                                                                        )
                                                                    ],
                                                                    spacing=0
                                                                ),
                                                                bgcolor=ft.colors.BACKGROUND,
                                                                padding=padding.symmetric(2,2),
                                                                border_radius=7,
                                                                height=240,
                                                                col=6,
                                                                visible=False
                                                            ),

                                                        ]
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
                                                                    content=Column(ref=self.column_product, alignment=MainAxisAlignment.SPACE_EVENLY),
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



    ## FUNÇÃO DE CONTROLE:

    def __required_fields(self, filds:list):

        """ Função para varrer e validar se há campos obrigatórios não preenchidos. """

        required = False
        for fild in filds:
            if fild.current.value == "" or fild.current.value == None:
                required = True
                fild.current.border_color=ft.colors.ERROR
            else:
                fild.current.border_color=ft.colors.OUTLINE

        self.update()
        return required

    def __clear_form(self, filds_text:list):

        """ Função para limpar todo o formulário de pedido """

        try:
            for fild in filds_text:
                try:
                    fild.current.value = None
                except Exception as e:
                    print(f'\n❌ ORDER_IMPORT > __clear_form() ==> EXCEPTION 1: {e}\n')
                    continue

            self.update()
            self.page.update()
            return None

        except Exception as e:
            print(f'\n❌ ORDER_IMPORT > __clear_form() ==> EXCEPTION 2: {e}\n')
            self.snackbar.internal_error()
            self.page.update()

    ## ---------


    ## FUNÇÃOS DE DADOS:

    def get_order(self, e):

        """ Função para obter os dados do pedido """

        try:
            self.button_attachment.current.disabled=True
            self.button_attachment.current.update()
            self.attachment_asana.current.disabled=True
            self.attachment_asana.current.value=False
            self.attachment_asana.current.update()
            self.order_commentUser.current.disabled=True
            self.order_commentUser.current.update()
            self.userComment_pinned.current.disabled=True
            self.userComment_pinned.current.value=False
            self.userComment_pinned.current.update()
            self.order_shippingDate.current.disabled=True
            self.order_shippingDate.current.update()
            self.page.update()

            self.__clear_form([self.order_number, self.order_channel, self.order_company, self.order_date, self.order_customer, self.order_customerNickname, self.order_shippingAddress, self.order_shippingMethod, self.order_shippingDate, self.order_commentUser])
            self.logo_channel.current.src = "assets/images/system/saleschannel_default.png"
            self.column_product.current.controls.clear()
            self.column_product.current.update()

            self.clear_uploads()

            verify_requiredFields = self.__required_fields([self.order_getNumber, self.order_getHub])
            if verify_requiredFields == True:
                self.snackbar.warning(msg="Favor, informar todos os campos obrigatórios para continuar.")
                self.order_getNumber.current.value, self.order_getHub.current.value, self.order_getCart.current.value, self.order_getShop.current.value, self.order_getCompany.current.value = None, None, '0', None, None
                self.order_ColumnShop.current.visible=False
                self.order_ColumnCompany.current.visible=False
                self.order_ColumnCart.current.visible=True
                self.update()
                self.page.update()
                return None

            self.alert.close_dialog()
            self.alert.progress_dialog("buscando pedido")
            self.page.dialog = self.alert
            self.alert.open = True
            self.page.update()

            #VALIDA SE O PEDIDO JÁ FOI IMPORTADO NO SISTEMA.
            verify_import = ORDER_REP().filter_number(self.order_getNumber.current.value.strip())
            if verify_import != None:
                self.alert.open = False
                self.snackbar.warning(msg=f"Pedido #{verify_import.order_number} já importado no sistema por {verify_import.order_userSystem} em {verify_import.order_date.strftime("%d/%m/%Y %H:%M:%S")}")
                self.order_getNumber.current.value, self.order_getHub.current.value, self.order_getCart.current.value, self.order_getShop.current.value, self.order_getCompany.current.value = None, None, '0', None, None
                self.order_ColumnShop.current.visible=False
                self.order_ColumnCompany.current.visible=False
                self.order_ColumnCart.current.visible=True
                self.update()
                self.page.update()
                return None

            if self.order_getCart.current.value == '1':
                print(f'\n🔍 NOVA BUSCA DE PEDIDO C/ CARRINHO IDERIS = #{self.order_getNumber.current.value}, por {self.user_system["name"]} em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
                get = ORDER(number=self.order_getNumber.current.value.strip(), hub=self.order_getHub.current.value, cart=True).verify_order()

            else:
                match self.order_getHub.current.value:
                    case "prestashop":
                        print(f'\n🔍 NOVA BUSCA DE PEDIDO ECOMMERCE = #{self.order_getNumber.current.value}, por {self.user_system["name"]} em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
                        get = ORDER(number=self.order_getNumber.current.value.strip(), hub=self.order_getHub.current.value, shop=self.order_getShop.current.value).verify_order()

                    case "shopee_api" | "shein_api" | "meli_api" | "magalu_api" | "americanas_api" | "tiny" | "tiktok_api":
                        print(f'\n[OK] NOVA BUSCA DE PEDIDO {self.order_getHub.current.value.upper()} = #{self.order_getNumber.current.value}, por {self.user_system["name"]} em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
                        get = ORDER(number=self.order_getNumber.current.value.strip(), hub=self.order_getHub.current.value, company=self.order_getCompany.current.value).verify_order()

                    case "magis5hub":
                        print(f'\n[OK] NOVA BUSCA DE PEDIDO MAGIS5 = #{self.order_getNumber.current.value}, por {self.user_system["name"]} em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
                        get = ORDER(number=self.order_getNumber.current.value.strip(), hub=self.order_getHub.current.value).verify_order()

                    case _:
                        print(f'\n🔍 NOVA BUSCA DE PEDIDO IDERIS = #{self.order_getNumber.current.value}, por {self.user_system["name"]} em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
                        get = ORDER(number=self.order_getNumber.current.value.strip(), hub=self.order_getHub.current.value).verify_order()


            if "Error" in get:
                self.alert.open = False
                self.snackbar.not_found(msg=f'Erro {get["Error"]["Code"]} - {get["Error"]["Message"]}')
                self.order_getNumber.current.value, self.order_getHub.current.value, self.order_getCart.current.value, self.order_getShop.current.value, self.order_getCompany.current.value = None, None, '0', None, None
                self.order_ColumnShop.current.visible=False
                self.order_ColumnCompany.current.visible=False
                self.order_ColumnCart.current.visible=True
                self.update()
                self.page.update()
                return None

            self.button_attachment.current.disabled=False
            self.button_attachment.current.update()
            self.attachment_asana.current.disabled=False
            self.attachment_asana.current.update()
            self.order_commentUser.current.disabled=False
            self.order_commentUser.current.update()
            self.userComment_pinned.current.disabled=False
            self.userComment_pinned.current.update()
            self.order_shippingDate.current.disabled=False
            self.order_shippingDate.current.update()
            self.page.update()

            self.__order_response = get
            self.__orderProduct_response = get['Products']

            self.order_number.current.value = f'#{get['orderNumber']} - {get["orderReference"]}' if get["orderReference"] != None else f'#{get['orderNumber']}'
            self.logo_channel.current.src = f"assets/images/system/{get['orderChannel']['name'].replace(" ", "").lower()}.png"
            self.order_channel.current.value = get['orderChannel']["name"]
            self.order_company.current.value = get['orderCompany']["name"]

            self.order_date.current.value = get['orderDate'].strftime('%d/%m/%Y %H:%M:%S') if self.order_getHub.current.value != "tiny" else get['orderDate'].strftime('%d/%m/%Y')

            self.order_customer.current.value = get['customer']
            self.order_customerNickname.current.value = get["customerNickname"]
            self.order_shippingAddress.current.value = get['shippingAddress']['enderecoCompleto']
            self.order_shippingMethod.current.value = get['shippingMethod']["name"] if get['shippingMethod']["name"] != "" else ""

            self.order_shippingDate.current.value = get['shippingDate'].strftime("%d/%m/%Y %H:%M:%S") if get['shippingDate'] != None else None
            # self.order_shippingDate.current.disabled = True if get['shippingDate'] != None else None

            self.order_commentSystem = f'Pedido {get["orderChannel"]["name"]} #{get["orderNumber"]}, importado de {get["hub"].upper()} | {self.app_config["app"]["name"]} v{self.app_config["app"]["version"]} - {self.app_config["app"]["build"]}'

            index_product = 1
            for product in self.__orderProduct_response:
                self.column_product.current.controls.append(
                    Container(
                        content=Column(
                            controls=[
                                ft.ListTile(
                                    leading=Container(
                                        content=ft.Image(src=product['icon'] if product['icon'] != "#" else "assets/images/system/nopreview.png", fit=ImageFit.FILL, border_radius=border_radius.all(100), ref=self.img_product),
                                        data={"index": index_product, "img": product['icon']},
                                        on_hover=self.hover_img_product,
                                        ref=self.container_img_product,
                                        padding=padding.all(0),
                                        margin=margin.all(0),
                                        height=80,
                                        width=60
                                    ),
                                    title=Text(value=f'{product['produto']}'.upper(), size=14, weight=ft.FontWeight.W_700, color=ft.colors.PRIMARY),
                                    subtitle=Column(
                                        controls=[
                                            Row(
                                                controls=[
                                                    Text(value="SKU:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                                    Text(value=product['sku'], size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                                ]
                                            ),
                                            Row(
                                                controls=[
                                                    Text(value="QUANTIDADE:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                                    Text(value=f"{product['qtd']} UND" if product['qtd'] == 1 else f"{product['qtd']} UNDS", size=12, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND),
                                                ]
                                            ),
                                        ],
                                        spacing=1
                                    ),
                                    content_padding=padding.symmetric(horizontal=0),
                                ),
    
                                TextField(
                                    value=product['personalizacao'],
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
                                    on_change=self.salve_customization
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

            self.column_product.current.update()

            self.alert.open = False
            self.order_getNumber.current.value, self.order_getHub.current.value, self.order_getCart.current.value, self.order_getShop.current.value, self.order_getCompany.current.value = None, None, '0', None, None
            self.order_ColumnShop.current.visible=False
            self.order_ColumnCompany.current.visible=False
            self.order_ColumnCart.current.visible=True
            self.update()
            self.page.update()

        except Exception as exc:
            print(f'\n[ERRO] ORDER_IMPORT > get_order() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def salve_customization(self, e):

        """ Função para salvar a nova personalização do produto """

        data_customize = e.control.data
        self.__orderProduct_response[int(data_customize)-1]['personalizacao'] = e.control.value
        self.page.update()


    def open_calendar(self, e):
        """ Calendário para selecionar data de envio """

        self.page.dialog = self.calend
        self.calend.open = True
        self.page.update()


    def select_date(self, e):

        """ Função para obter a data escolhida no calendário e atualizar o formulário do pedido """

        self.selected = e.control.data
        self.calend.close_dialog()
        self.order_shippingDate.current.value = f'{self.selected["day"]:02}/{self.selected["month"]:02}/{self.selected["year"]}'
        self.update()
        self.page.update()


    def pre_save(self, e):

        if self.order_shippingDate.current.value == "" or self.order_shippingDate.current.value == None:
            self.snackbar.warning("Informar uma DATA DE ENVIO para continuar!")
            self.page.update()
            return None

        for product in self.__orderProduct_response:
            if product['icon'] == "#":
                self.snackbar.warning("Há produto(s) SEM IMAGEM DEFINIDA. Anexe uma imagem para continuar!")
                self.page.update()
                return None

        if len(self.__orderProduct_response) > 1:
            self.alert.info_dialog(
                text="Pedido com mais de um produto.\nDeseja dividir em mais de uma tarefa?",
                act=[
                    btn(page=self.page, text="Sim", color="primary", style="small", event=self.task_divider),
                    btn(page=self.page, text="Não", color="warning", style="small", event=self.save_order)
                ]
            )
            self.page.dialog = self.alert
            self.alert.open = True
            self.page.update()
            return None

        else:
            print(f'\n▶️  NOVA IMPORTAÇÃO INICIADA = #{self.order_number.current.value}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
            self.save_order(None)


    def task_divider(self, e):

        self.index_product = 0
        self.partitions = 0
        self.divider_list = list()

        def add_partition(e):
            self.partitions +=1
            if self.partitions > 3:
                self.snackbar.warning(msg="Limite máximo de partições atingido.")
                self.page.update()
                return None
            self.product_divider.current.columns.append(DataColumn(Text(f'PARTE {self.partitions}', color=ft.colors.BACKGROUND)))
            for indice, linha in enumerate(self.product_divider.current.rows):
                linha.cells.append(
                    DataCell(
                        Checkbox(
                            check_color=ft.colors.BACKGROUND,
                            fill_color={"selected": ft.colors.LIGHT_GREEN_700},
                            data={"index": indice, "partition": self.partitions},
                            on_change=selected,                    
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
                            DataTable(
                                width=2600,
                                column_spacing=50,
                                vertical_lines=BorderSide(1, ft.colors.OUTLINE),
                                data_row_color={"hovered": ft.colors.SECONDARY_CONTAINER},
                                # data_row_height=65,
                                heading_row_color= ft.colors.SECONDARY,
                                heading_row_height=35,
                                show_bottom_border=True,
                                columns=[
                                    DataColumn(Text("Produto", color=ft.colors.BACKGROUND)),
                                ],
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

        for product in self.__orderProduct_response:
            self.product_divider.current.rows.append(DataRow(cells=[DataCell(Text(f'{product["produto"]} ({product["personalizacao"]})'))]))

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
                                FloatingActionButton(
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

        if len(self.divider_list) < len(self.__orderProduct_response):
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
        self.alert.progress_dialog("importando pedido")
        self.page.dialog = self.alert
        self.alert.open = True
        self.page.update()

        try:
            ORDER = ORDER_REP()
            if ORDER.filter_number(self.__order_response["orderNumber"]) != None:
                self.snackbar.warning("Pedido já importado no sistema.")

                self.__clear_form([self.order_number, self.order_channel, self.order_company, self.order_date, self.order_customer, self.order_customerNickname, self.order_shippingAddress, self.order_shippingMethod, self.order_shippingDate, self.order_commentUser])
                self.logo_channel.current.src = "assets/images/system/saleschannel_default.png"
                self.column_product.current.controls.clear()
                self.column_product.current.update()
                self.alert.open = False
                self.page.update()
                self.clear_uploads()
                return None

            self.asana_gid = list()
            self.copy_products = list()

            self.__save_DB(asana={"gid": []}) ## SAVE_DB
            id_order = ORDER.filter_number(self.__order_response["orderNumber"])

            if id_order != None:
                for part in range(int(self.partitions)):
                    for product in self.divider_list:
                        if product["product"]["partition"] == (part+1):
                            index = product["product"]["index"]
                            self.copy_products.append(self.__orderProduct_response[index])

                    task = self.__save_task(partition=[part+1, self.partitions]) ##SAVE_TASK
                    self.asana_gid.append(task["data"]["gid"])
                    self.copy_products.clear()

                ORDER.update(id=id_order.id, fild="order_task", data={"gid": self.asana_gid})

                if self.__order_response["orderChannel"]["name"] == "Prestashop":
                    PS().create_order_in_magis5(
                        order_number=self.__order_response["orderNumber"],
                        shop_id=self.__order_response["orderReference"][1]
                    )

                print(f'\n🧾 NOVO PEDIDO IMPORTADO = #{self.order_number.current.value}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')

            else:
                self.snackbar.internal_error()
                self.page.update()

            self.__clear_form([self.order_number, self.order_channel, self.order_company, self.order_date, self.order_customer, self.order_customerNickname, self.order_shippingAddress, self.order_shippingMethod, self.order_shippingDate, self.order_commentUser])
            self.logo_channel.current.src = "assets/images/system/saleschannel_default.png"
            self.column_product.current.controls.clear()
            self.column_product.current.update()
            self.alert.open = False
            self.page.update()
            self.clear_uploads()
            self.view_order() if id_order != None else None

        except Exception as ex:
            print(f'\n❌ EXCEPTION IN TASK_SAVEDIVIDER() ==> {ex}\n')
            order = ORDER_REP().filter_number(self.__order_response["orderNumber"])
            if order != None:
                if len(order.order_task["gid"]) == 0:
                    self.snackbar.internal_error()
    
                else:
                    self.snackbar.internal_error()
    
            else:
                self.snackbar.internal_error()


            self.__clear_form([self.order_number, self.order_channel, self.order_company, self.order_date, self.order_customer, self.order_customerNickname, self.order_shippingAddress, self.order_shippingMethod, self.order_shippingDate, self.order_commentUser])
            self.logo_channel.current.src = "assets/images/system/saleschannel_default.png"
            self.column_product.current.controls.clear()
            self.column_product.current.update()
            self.alert.open = False
            self.page.update()
            self.clear_uploads()


    def save_order(self, e):

        print(f'\n▶️  NOVA IMPORTAÇÃO INICIADA = #{self.order_number.current.value}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
        self.alert.close_dialog()
        self.alert.progress_dialog("importando pedido")
        self.page.dialog = self.alert
        self.alert.open = True
        self.page.update()

        try:
            ORDER = ORDER_REP()
            if ORDER.filter_number(self.__order_response["orderNumber"]) != None:
                self.snackbar.warning("Pedido já importado no sistema.")
                self.__clear_form([self.order_number, self.order_channel, self.order_company, self.order_date, self.order_customer, self.order_customerNickname, self.order_shippingAddress, self.order_shippingMethod, self.order_shippingDate, self.order_commentUser])
                self.logo_channel.current.src = "assets/images/system/saleschannel_default.png"
                self.column_product.current.controls.clear()
                self.column_product.current.update()
                self.alert.open = False
                self.page.update()
                self.clear_uploads()
                return None

            self.__save_DB(asana={"gid": []}) ## SAVE_DB
            id_order = ORDER.filter_number(self.__order_response["orderNumber"])
            if id_order != None:
                task = self.__save_task() ## SAVE_TASK
                ORDER.update(id=id_order.id, fild="order_task", data={"gid": [task["data"]["gid"]]})

                if self.__order_response["orderChannel"]["name"] == "Prestashop":
                    PS().create_order_in_magis5(
                        order_number=self.__order_response["orderNumber"],
                        shop_id=self.__order_response["orderReference"][1]
                    )

                print(f'\n🧾 NOVO PEDIDO IMPORTADO = #{self.order_number.current.value}, em {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n')
            else:
                self.snackbar.internal_error()
                self.page.update()

            self.__clear_form([self.order_number, self.order_channel, self.order_company, self.order_date, self.order_customer, self.order_customerNickname, self.order_shippingAddress, self.order_shippingMethod, self.order_shippingDate, self.order_commentUser])
            self.logo_channel.current.src = "assets/images/system/saleschannel_default.png"
            self.column_product.current.controls.clear()
            self.column_product.current.update()
            self.alert.open = False
            self.page.update()
            self.clear_uploads()
            self.view_order() if id_order != None else None

        except Exception as ex:
            print(f'\n[ERRO] EXCEPTION IN SAVE_ORDER() ==> {ex}\n')
            order = ORDER_REP().filter_number(self.__order_response["orderNumber"])
            if order != None:
                if len(order.order_task["gid"]) == 0:
                    self.snackbar.internal_error()
    
                else:
                    self.snackbar.internal_error()
    
            else:
                self.snackbar.internal_error()


            self.__clear_form([self.order_number, self.order_channel, self.order_company, self.order_date, self.order_customer, self.order_customerNickname, self.order_shippingAddress, self.order_shippingMethod, self.order_shippingDate, self.order_commentUser])
            self.logo_channel.current.src = "assets/images/system/saleschannel_default.png"
            self.logo_channel.current.update()
            self.column_product.current.controls.clear()
            self.column_product.current.update()
            self.alert.open = False
            self.page.update()
            self.clear_uploads()


    def __save_task(self, partition:list=None):

        # try:
        #     company = COMPANY().filter_id(self.__order_response["orderCompany"]["id"])
        #     get_date = datetime.strptime(self.order_shippingDate.current.value, '%d/%m/%Y %H:%M:%S')
        # except Exception as exc:
        #     print(f'\n❌ ORDER_IMPORT > __SAVE_TASK() ==> EXCEPTION 1: {exc}\n')
        #     get_date = datetime.strptime(self.order_shippingDate.current.value, '%d/%m/%Y')

        try:
            company = COMPANY().filter_id(self.__order_response["orderCompany"]["id"])
            get_date = datetime.strptime(self.order_shippingDate.current.value, '%d/%m/%Y %H:%M:%S')

        except Exception as exc:
            #print(f'\n❌ ORDER_IMPORT > __SAVE_TASK() ==> EXCEPTION 1: {exc}\n')
            get_date = datetime.strptime(self.order_shippingDate.current.value, '%d/%m/%Y')


        tag_rj = False if self.__order_response["shippingAddress"]["uf"] != "RJ" and self.__order_response["shippingAddress"]["uf"] != "Rio de Janeiro" else True


        data = {
            "completion_date": get_date,
            "project": "arte_final",
            "custom_fields": {
                "channel": self.__order_response["orderChannel"]["id"],
                "company": company.asanaID,
                "attendant": self.user_system["asanaID"],
                "shippingMethod": self.__order_response["shippingMethod"]["id"]
            },
            "info": {
                "number": self.__order_response["orderNumber"] if self.__order_response["orderReference"] == None else f'{self.__order_response["orderReference"]} ({self.__order_response["orderNumber"]})',
                "customer": self.__order_response["customer"],
                "date": self.order_date.current.value,
                "channel": self.__order_response["orderChannel"]["name"],
                "company": company.name,
                "attendant": self.user_system["name"],
                "address": self.order_shippingAddress.current.value,
                "shippingMethod": self.__order_response["shippingMethod"]["name"],
                "products": self.__orderProduct_response if partition == None else self.copy_products
            },
            "comments": [
                {"text": self.order_commentSystem, "pinned" : False},
                {"text": self.order_commentUser.current.value, "pinned" : self.userComment_pinned.current.value}
            ],
            # "tags": {
            #     "#RJ":tag_rj
            # }
        }

        if partition != None:
            create = TASK().create(type_body="order", task_data=data, partition=f'[Parte {partition[0]}/{partition[1]}]')
        else:
            create = TASK().create(type_body="order", task_data=data)

        return create


    def __save_DB(self, asana:dict):

        try:

            try:
                get_dateShipping = datetime.strptime(self.order_shippingDate.current.value, '%d/%m/%Y %H:%M:%S')
            except Exception as exc:
                print(f'\n❌ ORDER_IMPORT > __SAVE_DB() ==> EXCEPTION 1: {exc}\n')
                get_dateShipping = datetime.strptime(self.order_shippingDate.current.value, '%d/%m/%Y')

            get_original_dateShipping = self.__order_response["original_shippingDate"] if self.__order_response["original_shippingDate"] != None else null()

            db = ORDER_REP().insert(
                order_status="Importado",
                order_dateImport=DATE(),
                order_userSystem=self.user_system["name"],
                order_number=self.__order_response["orderNumber"],
                order_reference=null() if self.__order_response["orderReference"] == None else self.__order_response["orderReference"],
                order_channel=self.__order_response["orderChannel"]["name"],
                order_company=self.__order_response["orderCompany"]["name"],
                order_date=self.__order_response['orderDate'],
                order_customer=self.__order_response["customer"],
                order_customerID=self.__order_response["customerID"] if self.__order_response["customerID"] != None else null(),
                order_customerNickname=self.__order_response["customerNickname"] if self.__order_response["customerNickname"] != None else null(),
                order_customerPhone=self.__order_response['customerPhone'] if self.__order_response['customerPhone'] != None else null(),
                order_customerEmail=null(),
                order_shippingAddress=self.__order_response["shippingAddress"],
                order_shippingMethod=self.__order_response["shippingMethod"]["name"],
                order_shippingDate=get_dateShipping,
                order_shippingDateMKP=get_original_dateShipping,
                order_shippingTracking=self.__order_response["shippingTracking"] if self.__order_response["shippingTracking"] != "" else null(),
                order_task=asana,
                order_historic=self.order_commentSystem
            )

            for product in self.__orderProduct_response:
                ORDER_PRD().insert(
                    order_number=self.__order_response["orderNumber"],
                    name=product["produto"],
                    sku=product["sku"],
                    qty=product["qtd"],
                    icon=product["icon"],
                    customization=product["personalizacao"]
                )

            if len(self.order_commentUser.current.value) != 0:
                NOTE().insert(
                    module="order",
                    reference=self.__order_response["orderNumber"],
                    text=self.order_commentUser.current.value,
                    user=self.user_system["name"],
                    date=DATE()
                )

        except Exception as e:
            print(f'\n❌ ORDER_IMPORT > __SAVE_DB() ==> EXCEPTION 2: {e}\n')
            self.snackbar.internal_error()
            self.page.update()


    ## ---------

    def close_dialog(self, e):
        self.alert.open = False
        self.alert.actions = None
        self.alert.title = None
        self.alert.content = None
        self.page.update()


    def valide_integration(self, e):

        match e.control.value:
            case "prestashop":
                self.order_ColumnShop.current.visible=True
                self.order_ColumnCompany.current.visible=False
                self.order_ColumnCart.current.visible=False
                self.order_getCart.current.value='0'

            case "tiny":
                self.order_ColumnCompany.current.visible=True
                self.order_ColumnShop.current.visible=False
                self.order_ColumnCart.current.visible=False
                self.order_getCart.current.value='0'

            case "shopee_api" | "meli_api" | "shein_api" | "magalu_api" | "americanas_api" | "tiktok_api":
                self.order_ColumnCompany.current.visible=True
                self.order_ColumnShop.current.visible=False
                self.order_ColumnCart.current.visible=False
                self.order_getCart.current.value='0'  

            case _:
                self.order_ColumnCart.current.visible=True
                self.order_ColumnCompany.current.visible=False
                self.order_ColumnShop.current.visible=False
                self.order_getCart.current.value='0'

        self.update()
        self.page.update()


    def view_order(self):
        order = ORDER_REP().filter_number(self.__order_response["orderNumber"])
        if order == None:
            self.snackbar.internal_error()
            self.page.update()
            return None
        order_id = order.id
        self.page.session.set("order", order_id)
        self.page.go("/visualizar-pedido")


    def hover_img_product(self, e):

        self.product_image.data = e.control.data["index"]
        e.control.content = ft.IconButton(
            icon=icons.ADD_PHOTO_ALTERNATE_OUTLINED,
            icon_size=30,
            on_click=lambda _: self.product_image.pick_files(
                dialog_title="Escolher imagem do produto",
                initial_directory="/Desktop",
                allowed_extensions=["jpg", "jpeg", "png"],
                allow_multiple=False
            )
        ) if e.data == "true" else ft.Image(src=e.control.data["img"] if e.control.data["img"] != "#" else "assets/images/system/nopreview.png", fit=ImageFit.FILL, border_radius=border_radius.all(100), ref=self.img_product)

        e.control.update()
        self.page.update


    ## UPLOAD EVENTS ------

    def product_image_result(self, e:ft.FilePickerResultEvent):

        try:
            print(f'\nGET PRODUCT IMAGEM ==> {e.files} | {e.path}\n') ##DEBUG
            upload_list = []
            if self.product_image.result != None and self.product_image.result.files != None:
                for f in self.product_image.result.files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            f.name,
                            upload_url=self.page.get_upload_url(f'/{self.__order_response["orderNumber"]}/product/{f.name}', 600),
                        )
                    )
                self.product_image.upload(upload_list)

        except Exception as exc:
            print(f'\norder_import.py > product_image_result() ==> {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def product_image_progress(self, e:ft.FilePickerUploadEvent):

        try:
            if e.error == None:
                if e.progress == 1.0:
                    self.column_product.current.controls[e.control.data-1].content.controls[0].leading.content.src = f'upload/{self.__order_response["orderNumber"]}/product/{e.file_name}'
                    self.column_product.current.controls[e.control.data-1].content.controls[0].leading.data["img"] = f'upload/{self.__order_response["orderNumber"]}/product/{e.file_name}'
                    self.__orderProduct_response[e.control.data-1]['icon'] = f'assets/images/thumbnails/{e.file_name}'
                    self.img_product.current.update()
                    self.page.update()
                    print(f'\nIMAGEM DO PRODUTO ALTERADA ==> {self.__orderProduct_response[e.control.data-1]}\n')

                else:
                    return None

            else:
                print(f'\nERRO DE UPLOAD > product_image_progress() ==> {e.error}\n') #DEBUG
                self.snackbar.internal_error()
                self.page.update()

        except Exception as exc:
            print(f'\norder_import.py > product_image_progress() ==> {exc}\n') #DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def attachment_result(self, e:ft.FilePickerResultEvent):

        try:
            upload_list = []
            if self.attachment_file.result != None and self.attachment_file.result.files != None:
                for f in self.attachment_file.result.files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            f.name,
                            upload_url=self.page.get_upload_url(f'/{self.__order_response["orderNumber"]}/attachment/{f.name}', 600),
                        )
                    )
                    self.text_attachment.current.value = self.text_attachment.current.value + f'{f.name}\n'
                    self.text_attachment.current.update()

                self.attachment_file.upload(upload_list)

            self.page.update()

        except Exception as exc:
            print(f'\norder_import.py > attachment_result() ==> {exc}\n') #DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def attachment_progress(self, e:ft.FilePickerUploadEvent):

        try:
            if e.error != None:
                print(f'\nERRO DE UPLOAD > attachment_progress() ==> {e.error}\n') #DEBUG
                self.snackbar.internal_error()
                self.page.update()

        except Exception as exc:
            print(f'\norder_import.py > attachment_progress() ==> {exc}\n') #DEBUG
            self.snackbar.internal_error()
            self.page.update()

    ## ------


    def clear_uploads(self):
        try:
            if self.__order_response != None:
                path_dir = f'upload/{self.__order_response['orderNumber']}'
                if os.path.isdir(path_dir):
                    shutil.rmtree(path=path_dir, ignore_errors=True)

        except Exception as exc:
            print(f'\norder_import.py > clear_uploads() ==> {exc}\n') #DEBUG

import os, shutil, time, random, hashlib, base64
import flet as ft
from flet import (
    Page, UserControl, Ref,
    Column, Row, ResponsiveRow, Container, Divider,
    DataTable, DataColumn, DataRow, DataCell,
    Text, TextStyle, TextField, Dropdown, Checkbox, IconButton, FloatingActionButton, Image, ImageFit,
    Icon, MainAxisAlignment, CrossAxisAlignment, BorderSide,
    dropdown, icons, margin, padding, alignment, border_radius
)

from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

## Conexão com Dados
from data.repository.orderV2 import OrderRepositoryV2 as ORDER_REP
from data.repository.order_product import OrderProductRepository as ORDER_PRD
from data.repository.saleschannel import SalesChannelRepository as CHANNEL
from data.repository.warranty import WarrantyRepository as WR
from data.repository.warranty_product import WarrantyProductRepository as WRP
from data.repository.warranty_reason import WarrantyReasonRepository as WRR
from data.repository.commentsV2 import CommentsV2Repository as NOTE
from data.repository.status import StatusRepository as STATUS
from data.repository.company import CompanyRepository as COMPANY
from data.repository.carrier import CarrierRepository as CARRIER
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

from source.api.magis5 import Magis5


class NewWarranty(UserControl):

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
        self.get_orderNumber = Ref[TextField]()

        self.set_logoChannel = Ref[Image]()
        self.set_orderNumber = Ref[Text]()
        self.set_orderChannel = Ref[TextField]()
        self.set_orderCompany = Ref[TextField]()
        self.set_orderDate = Ref[TextField]()
        self.set_orderCustomer = Ref[TextField]()
        self.set_orderShipping_address = Ref[TextField]()
        self.set_orderShipping_number = Ref[TextField]()
        self.set_orderShipping_district = Ref[TextField]()
        self.set_orderShipping_city = Ref[TextField]()
        self.set_orderShipping_state = Ref[TextField]()
        self.set_orderShipping_zipcode = Ref[TextField]()
        self.set_orderShipping_complement = Ref[TextField]()
        self.set_orderShipping_receiver = Ref[TextField]()
        self.set_orderShipping_phone = Ref[TextField]()

        self.set_orderShipping_carrier = Ref[Dropdown]()
        self.set_orderShipping_date = Ref[TextField]()

        self.set_list_products = Ref[Dropdown]()
        self.set_button_append_product = Ref[FloatingActionButton]()
        self.set_column_append_product = Ref[Column]()
        self.set_product_img = Ref[Image]()
        self.set_product_qty = Ref[TextField]()
        self.set_product_note = Ref[TextField]()
        self.set_new_products = list()

        self.set_list_reasons = Ref[Dropdown]()
        self.set_text_reason = Ref[Text]()
        self.set_reason_notes = Ref[TextField]()
        self.set_image_attachment = Ref[Row]()
        self.set_image_buttonAttch = Ref[FloatingActionButton]()
        self.list_image_attachment = list()

        self.column_form_order = Ref[Column]()

        ## ---------

        self.attachment_warranty = ft.FilePicker(on_result=self.attachment_result, on_upload=self.attachment_progress)
        self.page.overlay.append(self.attachment_warranty)

        self.product_image = ft.FilePicker(on_result=self.product_image_result, on_upload=self.product_image_progress)
        self.page.overlay.append(self.product_image)



    def build(self):

        # self.page.floating_action_button = ft.FloatingActionButton(icon=ft.icons.ADD)
        # self.page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

        set_order = self.content_order()
        set_attatment = self.content_reason()

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
                                                        Text(value="Buscar Pedido", size=13, weight="w700", color=ft.colors.ON_BACKGROUND)
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
                                                    ref=self.get_orderNumber,
                                                ),
                                            ],
                                            spacing=5
                                        ),

                                        ft.IconButton(icon=icons.SEARCH, bgcolor=ft.colors.SECONDARY_CONTAINER, on_click=self.get_order)
                                    ],
                                    vertical_alignment=CrossAxisAlignment.END
                                ),
                                Row(controls=[
                                        btn(page=self.page, icon="save", text="salvar", style="small", color="primary", event=self.valida_form)
                                    ]
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        ),
                        bgcolor=ft.colors.BACKGROUND,
                        padding=padding.symmetric(20,30)
                    ),

                    Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.15),

                    ## FORMULÁRIO GARANTIA
                    Container(
                        content=Column(
                            ref=self.column_form_order,
                            controls=[
                                ResponsiveRow(
                                    controls=[set_order, set_attatment],
                                    vertical_alignment=CrossAxisAlignment.START,
                                    spacing=0
                                )
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

    ## ---------


    ## FUNÇÃOS DE DADOS:


    def get_order(self, e):

        """ Buscar pedidos no sistema. """

        try:
            self.__clear_form()
            order_number = self.get_orderNumber.current.value
            self.getOrder = ORDER_REP().filter_number(order_number)
            # print(f'\nW_NEW > getOrder() ==> PEDIDO: {self.getOrder}\n') ##DEBUG

            if self.getOrder==None:
                self.getOrder = ORDER_REP().filter_reference(order_number)
                if self.getOrder==None:
                    self.snackbar.not_found(f'Pedido num. "{order_number}" não encontrado no Fadrix SYS.')
                    return None

            self.set_logoChannel.current.src = CHANNEL().filter_name(self.getOrder.order_channel).icon
            self.set_orderNumber.current.value = self.getOrder.order_number if self.getOrder.order_reference==None else f'{self.getOrder.order_number}, {self.getOrder.order_reference}'
            self.set_orderChannel.current.value = self.getOrder.order_channel
            self.set_orderCompany.current.value = self.getOrder.order_company
            self.set_orderDate.current.value = self.getOrder.order_date.strftime("%d/%m/%Y %H:%M:%S")
            self.set_orderCustomer.current.value = self.getOrder.order_customer

            self.set_orderShipping_address.current.value = self.getOrder.order_shippingAddress["endereco"]
            self.set_orderShipping_address.current.disabled=False
            self.set_orderShipping_number.current.value = self.getOrder.order_shippingAddress["numero"]
            self.set_orderShipping_number.current.disabled=False
            self.set_orderShipping_district.current.value = self.getOrder.order_shippingAddress["bairro"]
            self.set_orderShipping_district.current.disabled=False
            self.set_orderShipping_city.current.value = self.getOrder.order_shippingAddress["cidade"]
            self.set_orderShipping_city.current.disabled=False
            self.set_orderShipping_state.current.value = self.getOrder.order_shippingAddress["uf"]
            self.set_orderShipping_state.current.disabled=False
            self.set_orderShipping_zipcode.current.value = self.getOrder.order_shippingAddress["cep"]
            self.set_orderShipping_zipcode.current.disabled=False
            self.set_orderShipping_complement.current.value = self.getOrder.order_shippingAddress["complemento"]
            self.set_orderShipping_complement.current.disabled=False
            self.set_orderShipping_receiver.current.value = self.getOrder.order_shippingAddress["destinatario"]
            self.set_orderShipping_receiver.current.disabled=False
            self.set_orderShipping_phone.current.value = self.getOrder.order_customerPhone
            self.set_orderShipping_phone.current.disabled=False

            self.getCarriers = CARRIER().filter_all()
            if len(self.getCarriers) != 0:
                self.set_orderShipping_carrier.current.options = [dropdown.Option(key=carrier.id, text=f'{carrier.name}') for carrier in self.getCarriers if carrier.id in [10,11,12]]
                self.set_orderShipping_carrier.current.disabled=False
                self.set_orderShipping_date.current.disabled=False


            self.getProduct = ORDER_PRD().filter_number(self.getOrder.order_number)
            # print(f'\nW_NEW > getOrder() ==> PRODUTOS: {self.getProduct}\n') ##DEBUG
            if len(self.getProduct) != 0:
                self.set_list_products.current.options = [dropdown.Option(key=self.getProduct.index(item), text=f'{item.name} | {item.sku}') for item in self.getProduct]
                self.set_list_products.current.disabled=False
                self.set_button_append_product.current.disabled=False


            self.getReason = WRR().filter_all()
            # print(f'\nW_NEW > getOrder() ==> REASON: {self.getReason}\n') ##DEBUG
            self.getReason.reverse()
            reason_options = [dropdown.Option(key=reason.id, text=f'{reason.id}. {reason.reason}') for reason in self.getReason]
            self.set_list_reasons.current.options = reason_options
            self.set_list_reasons.current.disabled = False
            self.set_reason_notes.current.disabled = False
            self.set_image_buttonAttch.current.disabled = False


            self.get_orderNumber.current.value = None #Limpa o campo de busca de pedidos.
            self.update()
            self.page.update()

        except Exception as exc:
            print(f'\n❌ W_NEW > getOrder() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            return None


    def content_order(self) -> Container:

        """ Cria o conteúdo com as informações do pedido. """

        return Container(
            content=Column(
                controls=[

                    Container(
                        content=Column(
                            controls=[

                                Container(
                                    content=Text(value="Informações da Garantia", size=16, weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY),
                                    bgcolor=ft.colors.SECONDARY_CONTAINER,
                                    border_radius=border_radius.only(5,5),
                                    padding=padding.symmetric(10,20),
                                    alignment=alignment.center_left
                                ),

                                Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                Container(
                                    content=Row(
                                        controls=[
                                            ft.Image(src="assets/images/system/saleschannel_default.png", border_radius=100, width=30, ref=self.set_logoChannel),
                                            Text(value=None, size=18, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND, ref=self.set_orderNumber)
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

                                            # DADOS DO PEDIDO
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
                                                                ref=self.set_orderChannel,
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
                                                                ref=self.set_orderCompany,
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
                                                                ref=self.set_orderDate,
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
                                                                ref=self.set_orderCustomer,
                                                                disabled=True
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=12
                                                    ),
                                                ],
                                            ),

                                            Container(height=15),

                                            Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                            # DADOS PARA ENVIO
                                            Container(
                                                content=Text(value="DADOS PARA ENVIO", size=16, weight=ft.FontWeight.W_600, color=ft.colors.SURFACE_TINT),
                                                padding=padding.symmetric(15,0),
                                                alignment=alignment.center
                                                # height=15
                                            ),

                                            ResponsiveRow(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.LOCATION_ON, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Endereço", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_address,
                                                                height=35,
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
                                                                    Icon(name=icons.NUMBERS_ROUNDED, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Número", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_number,
                                                                height=35,
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
                                                                    Icon(name=icons.LOCATION_ON, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Bairro", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_district,
                                                                height=35,
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
                                                                    Icon(name=icons.LOCATION_ON, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Cidade", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_city,
                                                                height=35,
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
                                                                    Icon(name=icons.LOCATION_ON, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Estado", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_state,
                                                                height=35,
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
                                                                    Icon(name=icons.LOCATION_ON, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="CEP", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_zipcode,
                                                                height=35,
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
                                                                    Icon(name=icons.LOCATION_ON, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Complemento", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_complement,
                                                                height=35,
                                                                disabled=True
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=8
                                                    ),

                                                ],
                                            ),

                                            ResponsiveRow(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.PERSON_PIN, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Recebedor", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_receiver,
                                                                height=35,
                                                                disabled=True
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=7
                                                    ),                                                    
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.LOCAL_PHONE, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Tel. Contato", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_phone,
                                                                height=35,
                                                                disabled=True
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=5
                                                    ),
                                                ],
                                            ),

                                            ResponsiveRow(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.LOCAL_SHIPPING_OUTLINED, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Forma de Envio", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                content_padding=padding.symmetric(vertical=5, horizontal=10),
                                                                ref=self.set_orderShipping_carrier,
                                                                height=35,
                                                                disabled=True,
                                                                on_change=lambda e: print(e.control.value),
                                                                alignment=alignment.center_left
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=8
                                                    ),
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.CALENDAR_TODAY, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Data Prevista de Envio", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                ref=self.set_orderShipping_date,
                                                                height=35,
                                                                suffix=IconButton(icons.CALENDAR_MONTH, icon_size=18, icon_color=ft.colors.PRIMARY, width=30, height=30, on_click=self.open_calendar),
                                                                read_only=True,
                                                                disabled=True
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=4
                                                    ),

                                                ],
                                                vertical_alignment=CrossAxisAlignment.END
                                            ),                                            

                                            Container(height=15),

                                            Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                            # PRODUTOS PARA GARANTIA
                                            Container(
                                                content=Text(value="PRODUTOS PARA GARANTIA", size=16, weight=ft.FontWeight.W_600, color=ft.colors.SURFACE_TINT),
                                                padding=padding.symmetric(15,0),
                                                alignment=alignment.center
                                                # height=15
                                            ),

                                            ResponsiveRow(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.LIST, size=13, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Produtos do Pedido", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                content_padding=padding.symmetric(vertical=5, horizontal=10),
                                                                ref=self.set_list_products,
                                                                height=35,
                                                                disabled=True,
                                                                on_change=self.change_product,
                                                                alignment=alignment.center_left
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=11
                                                    ),

                                                    Column(
                                                        controls=[
                                                            ft.FloatingActionButton(
                                                                ref=self.set_button_append_product,
                                                                data=self.set_list_products.current.value,
                                                                icon=ft.icons.ADD,
                                                                bgcolor=ft.colors.PRIMARY,
                                                                width=40,
                                                                height=40,
                                                                on_click=self.append_product,
                                                                disabled=True
                                                            )
                                                        ],
                                                        spacing=5,
                                                        col=1
                                                    ),

                                                ],
                                                vertical_alignment=CrossAxisAlignment.END
                                            ),

                                            Container(height=15),

                                            ResponsiveRow(
                                                controls=[
                                                    Column(
                                                        ref=self.set_column_append_product,
                                                        spacing=5,
                                                        col=12
                                                    ),
                                                ],
                                            ),

                                            Container(height=15),

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

                ],
                spacing=15
            ),
            margin=margin.symmetric(15,15),
            col=7
        )


    def content_reason(self) -> Container:

        """ Cria o conteúdo com os motivos da garantia. """

        return Container(
            content=Column(
                controls=[

                    Container(
                        content=Column(
                            controls=[

                                Container(
                                    content=Text(value="Motivo da Garantia", size=16, weight=ft.FontWeight.W_500, color=ft.colors.PRIMARY),
                                    bgcolor=ft.colors.SECONDARY_CONTAINER,
                                    border_radius=border_radius.only(5,5),
                                    padding=padding.symmetric(10,20),
                                    alignment=alignment.center_left
                                ),

                                Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.1),

                                Container(
                                    content=Column(
                                        controls=[

                                            # DADOS DO PROBLEMA
                                            ResponsiveRow(
                                                controls=[

                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.ERROR_OUTLINE, size=14, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Relatar Problema", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                content_padding=padding.symmetric(vertical=5, horizontal=10),
                                                                ref=self.set_list_reasons,
                                                                alignment=alignment.center_left,
                                                                on_change=self.change_reason,
                                                                disabled=True
                                                            ),
                                                            Text(value=None, size=10, weight="w200", color=ft.colors.ON_BACKGROUND, ref=self.set_text_reason)
                                                        ],
                                                        spacing=5,
                                                        col=12
                                                    ),

                                                ],
                                            ),

                                            ResponsiveRow(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.SPEAKER_NOTES, size=14, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Observações do Problema", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                                                multiline=True,
                                                                min_lines=3,
                                                                max_lines=3,
                                                                ref=self.set_reason_notes,
                                                                disabled=True
                                                            ),
                                                        ],
                                                        spacing=5,
                                                        col=12
                                                    ),
                                                ],
                                            ),

                                            ResponsiveRow(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Row(
                                                                controls=[
                                                                    Icon(name=icons.IMAGE_OUTLINED, size=14, color=ft.colors.ON_BACKGROUND),
                                                                    Text(value="Fotos do Problemas", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                                                ],
                                                                spacing=3
                                                            ),
                                                            Container(
                                                                content=Row(
                                                                    ref=self.set_image_attachment,
                                                                    alignment=MainAxisAlignment.CENTER,
                                                                    vertical_alignment=CrossAxisAlignment.CENTER,
                                                                    scroll=ft.ScrollMode.ADAPTIVE
                                                                ),
                                                                height=300,
                                                                bgcolor=ft.colors.with_opacity(0.2, ft.colors.OUTLINE_VARIANT),
                                                                border_radius=10,
                                                                padding=padding.symmetric(10,10),
                                                                alignment=alignment.center
                                                            ),
                                                            ft.FloatingActionButton(
                                                                text="Anexar Imagem",
                                                                width=130,
                                                                mini=True,
                                                                on_click=lambda _: self.attachment_warranty.pick_files(
                                                                    dialog_title="Anexar",
                                                                    initial_directory="/Desktop",
                                                                    allow_multiple=False,
                                                                    allowed_extensions=["jpg", "jpeg", "png"]
                                                                ),
                                                                ref=self.set_image_buttonAttch,
                                                                disabled=True
                                                            )
                                                        ],
                                                        spacing=5,
                                                        col=12
                                                    ),
                                                ],
                                            ),

                                            Container(height=5),

                                        ],
                                        spacing=30
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

                ],
                spacing=15
            ),
            margin=margin.symmetric(15,15),
            col=5
        )


    def change_product(self, e):
        """ Escolher um produto da listagem orginal do pedido. """

        self.set_button_append_product.current.data = e.control.value
        self.set_button_append_product.current.update()
        self.update()


    def change_reason(self, e):

        """ Escolher um motivo da listagem de motivos de garantia. """

        reason = self.getReason[int(e.control.value)-1].reason
        self.set_text_reason.current.value = reason
        self.set_text_reason.current.update()
        self.page.update()


    def append_product(self, e):

        """ Adiciona um produto na garantia. """

        try:
            if e.control.data == None:
                self.snackbar.warning("Selecione um produto ao lado para poder ser adicionado na garantia!")
                self.page.update()
                return None

            index = int(e.control.data)
            product = self.getProduct[index]
            self.set_new_products.append([index, product.id])

            if self.set_list_products.current.options[index].disabled==True:
                self.snackbar.warning("Produto já adicionado na garantia!")
                return None

            self.set_list_products.current.options[index].disabled=True
            self.set_list_products.current.update()

            self.set_column_append_product.current.controls.append(
                Container(
                    content=ft.ListTile(
                        leading=Container(
                            content=ft.Image(src=product.icon, fit=ImageFit.FILL, border_radius=border_radius.all(100), error_content=Image(src="V4/assets/images/system/nopreview.png", fit=ImageFit.FILL, border_radius=border_radius.all(100)), ref=self.set_product_img),
                            data={"index": index, "img": product.icon},
                            padding=padding.all(0),
                            margin=margin.all(0),
                            height=80,
                            width=60,
                            on_hover=self.hover_img_product
                        ),
                        title=Container(
                            content=Text(value=f'{product.name} | {product.sku}'.upper(), size=14, weight=ft.FontWeight.W_700, color=ft.colors.PRIMARY),
                            margin=margin.symmetric(5)
                        ),
                        subtitle=ResponsiveRow(
                            controls=[
                                Column(
                                    controls=[
                                        Row(
                                            controls=[
                                                Icon(name=icons.NUMBERS_ROUNDED, size=14, color=ft.colors.ON_BACKGROUND),
                                                Text(value="Quantidade", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                            ],
                                            spacing=3
                                        ),
                                        TextField(
                                            value=None,
                                            text_style=TextStyle(size=16, weight="w600"),
                                            suffix_text="UND",
                                            color=ft.colors.ON_BACKGROUND,
                                            bgcolor=ft.colors.BACKGROUND,
                                            border_color=ft.colors.OUTLINE,
                                            border_radius=5,
                                            focused_color=ft.colors.PRIMARY,
                                            focused_border_color=ft.colors.PRIMARY,
                                            content_padding=padding.symmetric(vertical=1, horizontal=10),
                                            keyboard_type=ft.KeyboardType.NUMBER,
                                            ref=self.set_product_qty,
                                            height=35,
                                        ),
                                    ],
                                    spacing=5,
                                    col=2
                                ),
                                Column(
                                    controls=[
                                        Row(
                                            controls=[
                                                Icon(name=icons.EDIT_NOTE_ROUNDED, size=14, color=ft.colors.ON_BACKGROUND),
                                                Text(value="Observação sobre PRODUTO/PEÇA para enviar.", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
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
                                            ref=self.set_product_note,
                                            height=55,
                                            max_length=50
                                        ),
                                    ],
                                    spacing=5,
                                    col=10
                                ),                            
                            ],
                        ),
                        trailing=IconButton(icon=icons.DELETE_OUTLINE_ROUNDED, bgcolor=ft.colors.with_opacity(0.2, ft.colors.PRIMARY), data={"index_product": index, "id": product.id, "original_img": product.icon}, tooltip="Excluir", on_click=self.delete_product),
                        content_padding=padding.symmetric(horizontal=0),
                    ),
                    data=product.id,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=7,
                    padding=padding.symmetric(10,20),
                    margin=margin.symmetric(10)
                )
            )

            self.set_column_append_product.current.update()
            self.page.update()

        except Exception as exc:
            print(f'W_NEW > append_product() ==> ❌ Exception: {exc}')
            self.snackbar.internal_error()
            self.page.update()


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
        ) if e.data == "true" else ft.Image(src=e.control.data["img"] if e.control.data["img"] != "#" else "assets/images/system/nopreview.png", fit=ImageFit.FILL, border_radius=border_radius.all(100), ref=self.set_product_img)

        e.control.update()
        self.page.update


    def delete_product(self, e):

        """ Excluir um produto adicionado a garantia. """

        try:
            index_product = int(e.control.data["index_product"])
            index_column = e.control.data["id"]
            product_img_original = e.control.data["original_img"]
            product = self.getProduct[index_product]

            warranty_directory = Path(f'V4/assets/attachment/warranty/{self.getOrder.order_number}')
            warranty_attachment_directory = Path(f'V4/assets/attachment/warranty/{self.getOrder.order_number}/attachment')
            warranty_product_directory = Path(f'V4/assets/attachment/warranty/{self.getOrder.order_number}/product')

            if warranty_product_directory.exists():
                product_image = Path(product.icon)

                if product_image.exists():
                    match len(self.set_column_append_product.current.controls):

                        case 1:

                            if warranty_attachment_directory.exists():
                                try:
                                    shutil.rmtree(path=warranty_product_directory.resolve(), ignore_errors=True)
                                except Exception as exc:
                                    print(f'\n❌ N_NEW > delete_product() ==> EXCEPTION DELETE 0: {exc}\n') ##DEBUG
                                    self.snackbar.internal_error()
                                    self.page.update()
                                    return None

                            else:
                                try:
                                    shutil.rmtree(path=warranty_directory.resolve(), ignore_errors=True)
                                except Exception as exc:
                                    print(f'\n❌ N_NEW > delete_product() ==> EXCEPTION DELETE 1: {exc}\n') ##DEBUG
                                    self.snackbar.internal_error()
                                    self.page.update()
                                    return None

                        case _:

                            try:
                                os.remove(product_image.resolve())
                            except Exception as exc:
                                print(f'\n❌ N_NEW > delete_product() ==> EXCEPTION DELETE 2: {exc}\n') ##DEBUG
                                self.snackbar.internal_error()
                                self.page.update()
                                return None

                else:
                    print(f'\n❌ W_NEW > delete_product() ==> ERROR DELETE: ARQUIVO NÃO EXISTE NO DIRETÓRIO | PATH: {product_image}.\n') ##DEBUG
                    self.page.update()

            self.getProduct[index_product-1].icon = product_img_original
            self.set_list_products.current.options[index_product].disabled=False
            self.set_list_products.current.update()

            for pd in self.set_column_append_product.current.controls:
                if pd.data == index_column:
                    self.set_column_append_product.current.controls.pop(self.set_column_append_product.current.controls.index(pd))
                    self.set_column_append_product.current.update()

            # self.set_new_products.remove([index_product, index_column])
            self.page.update()

        except Exception as exc:
            print(f'\n❌ W_NEW > delete_product() ==>  EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()
            return None


    def __clear_form(self):
        """ Limpa todo o formulário de garantia. """

        try:
            self.set_logoChannel.current.src = "assets/images/system/saleschannel_default.png"

            filds_text = [self.set_orderNumber, self.set_orderChannel, self.set_orderCompany, self.set_orderDate, self.set_orderCustomer, self.set_orderShipping_address, self.set_orderShipping_number, self.set_orderShipping_district, self.set_orderShipping_city, self.set_orderShipping_state, self.set_orderShipping_zipcode, self.set_orderShipping_complement, self.set_orderShipping_receiver, self.set_orderShipping_phone, self.set_reason_notes, self.set_orderShipping_carrier, self.set_orderShipping_date]

            for fild in filds_text:
                fild.current.value = None
                fild.current.update()

            self.set_orderShipping_address.current.disabled=True
            self.set_orderShipping_number.current.disabled=True
            self.set_orderShipping_district.current.disabled=True
            self.set_orderShipping_city.current.disabled=True
            self.set_orderShipping_state.current.disabled=True
            self.set_orderShipping_zipcode.current.disabled=True
            self.set_orderShipping_complement.current.disabled=True
            self.set_orderShipping_receiver.current.disabled=True
            self.set_orderShipping_phone.current.disabled=True
            self.set_orderShipping_carrier.current.disabled=True
            self.set_orderShipping_date.current.disabled=True

            self.set_list_products.current.options.clear()
            self.set_list_products.current.disabled=True
            self.set_button_append_product.current.disabled=True

            self.set_list_reasons.current.options.clear()
            self.set_list_reasons.current.disabled=True
            self.set_reason_notes.current.disabled=True
            self.set_image_buttonAttch.current.disabled=True

            self.set_column_append_product.current.controls.clear()
            self.set_column_append_product.current.update()

            self.set_image_attachment.current.controls.clear()
            self.list_image_attachment.clear()

            self.clear_uploads()

            self.update()
            self.page.update()


        except Exception as exc:
            print(f'W_NEW > __clear_form() ==> ❌ Exception: {exc}')
            self.snackbar.internal_error()
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
        self.set_orderShipping_date.current.value = f'{self.selected["day"]:02}/{self.selected["month"]:02}/{self.selected["year"]}'
        self.update()
        self.page.update()


    ## SAVE EVENTS ------

    def valida_form(self, e):

        """ Valida se todos os dados de endereço para envio foram informados. """

        list_filds = [self.set_orderShipping_address, self.set_orderShipping_number, self.set_orderShipping_district, self.set_orderShipping_city, self.set_orderShipping_state, self.set_orderShipping_zipcode, self.set_orderShipping_receiver, self.set_orderShipping_phone, self.set_orderShipping_carrier, self.set_orderShipping_date]

        # VALIDA O ENDEREÇO DE ENVIO:
        for fild in list_filds:
            if len(fild.current.value) <= 1:
                print(f'\n💡 W_NEW > valida_endereco() ==> EMPTY FIELD: {fild.current.value}\n')
                self.snackbar.warning(f'Infomarções incompletas, não pode haver campos em branco ou com apenas 1 carater.')
                self.page.update()
                return None

        # VALIDA SE HÁ PRODUTOS ADICIONADO NA GARANTIA:
        if len(self.set_column_append_product.current.controls) == 0:
            self.snackbar.warning("Não foi adicionados produtos para garantia.")
            self.page.update()
            return None

        # VALIDA SE FOI INFORMADO QUANTIDADE PARA CADA PRODUTO:
        for produto in self.set_column_append_product.current.controls:
            if len(produto.content.subtitle.controls[0].controls[1].value) == 0:
                self.snackbar.warning("Informa quantidade de unds para todos os produtos da garantia.")
                self.page.update()
                return None

        # VALIDA DE FOI RELATADO (SELECIONAR) UM MOTIVO DA GARANTIA:
        if self.set_text_reason.current.value == None:
            self.snackbar.warning("Relatar qual o problema com o pedido selecionando uma opção na listagem.")
            self.page.update()
            return None

        # VALIDA SE FOI ADICIONADO IMAGEM COM PROVAS DO PROBLEMA:
        # if len(self.set_image_attachment.current.controls) == 0:
        #     self.snackbar.warning("Adicionar imagens do cliente com provas do problema relatado acima.")
        #     self.page.update()
        #     return None

        self.alert.progress_dialog("Criando Garantia ...")
        self.page.dialog=self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        today = datetime.now().astimezone(timezone("America/Sao_Paulo"))
        shipping_date = datetime.strptime(self.set_orderShipping_date.current.value, "%d/%m/%Y")
        print(f'\nshipping_date: {shipping_date} / {self.set_orderShipping_date.current.value}\n')
        sign = self.__sign()

        # save_DB = self.__save_DB(sign=sign, date=today, shipping_date=shipping_date)
        # if not save_DB:
        #     self.snackbar.internal_error()
        #     self.alert.open=False
        #     self.page.update()
        #     return None

        #warranty = WR().filter_order_and_sing(sign=sign, order=self.getOrder.order_number if self.getOrder.order_reference == None else self.getOrder.order_reference)
        save_TASK = self.__save_task(date_create=today, shipping_date=shipping_date)

        #WR().update(warranty.id, fild='task_id', data={"gid": [save_TASK["data"]["gid"]]})

        self.alert.open=False
        self.page.update()

        self.alert.progress_dialog("Enviando Garantia P/ Magis5 ... ")
        self.page.dialog=self.alert
        self.alert.open=True
        self.alert.modal=True
        self.page.update()

        import_magis5 = self.create_order_in_magis5(date_create=today)
        if not import_magis5:
            self.alert.open=False
            self.snackbar.warning(msg="Garantia não importada no Magis5, tente novamente.")
            self.page.update()
            return None

        else:
            self.__clear_form()
            self.alert.open=False
            self.page.update()


    def __save_DB(self, sign:str, date, shipping_date):

        """ Salva as informações da Garantia no Banco de Dados. """

        try:
            WR().insert(
                sign=sign,
                status="5",
                date=date,
                user=self.user_system["name"],
                order_ref=f'GRT-{self.getOrder.order_number}' if self.getOrder.order_reference == None else f'GRT-{self.getOrder.order_reference}',
                order_channel=self.getOrder.order_channel,
                order_buyer=self.getOrder.order_customer,
                shipping_address={"endereco": self.set_orderShipping_address.current.value, "numero": self.set_orderShipping_number.current.value, "complemento": self.set_orderShipping_complement.current.value, "bairro": self.set_orderShipping_district.current.value, "cidade": self.set_orderShipping_city.current.value, "uf": self.set_orderShipping_state.current.value, "cep": self.set_orderShipping_zipcode.current.value, "destinatario": self.set_orderShipping_receiver.current.value, "telefone": self.set_orderShipping_phone.current.value},
                shipping_method=self.set_orderShipping_carrier.current.value,
                shipping_date=shipping_date,
                shipping_tracking=null(),
                reason=self.set_list_reasons.current.value,
                liable=null(),
                note=self.set_reason_notes.current.value if self.set_reason_notes.current.value != None else null(),
                task_id={"gid": []},
                historic=f'Garantia {self.getOrder.order_channel} #{self.getOrder.order_number if self.getOrder.order_reference == None else self.getOrder.order_reference}, criada por {self.user_system["name"]} | {self.app_config["app"]["name"]} v{self.app_config["app"]["version"]} - {self.app_config["app"]["build"]}'
            )

            for index in self.set_new_products:
                for pd in self.set_column_append_product.current.controls:
                    if pd.data == index[1]:
                        pd_qtd = pd.content.subtitle.controls[0].controls[1].value
                        pd_note = pd.content.subtitle.controls[1].controls[1].value

                product = self.getProduct[int(index[0])]

                WRP().insert(
                    sign=sign,
                    order_ref=f'GRT-{self.getOrder.order_number}' if self.getOrder.order_reference == None else f'GRT-{self.getOrder.order_reference}',
                    name=product.name,
                    sku=product.sku,
                    qty=pd_qtd,
                    icon=product.icon,
                    customization=product.customization if product.customization != None else null(),
                    note=pd_note if pd_note != None and pd_note != "" else null()
                )

            for img in self.list_image_attachment:
                NOTE().insert(
                    sign=sign,
                    module="warranty",
                    reference=f'GRT-{self.getOrder.order_number}' if self.getOrder.order_reference == None else f'GRT-{self.getOrder.order_reference}',
                    user=self.user_system["name"],
                    date=date,
                    type_msg="image",
                    text=null(),
                    sticker=null(),
                    image=str(img),
                    audio=null(),
                    video=null(),
                    attachment=null(),
                    reply=null()
                )

            return True

        except Exception as exc:
            print(f'\n❌ W_NEW > __save_DB() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()
            return False


    def __save_task(self, date_create:datetime, shipping_date:datetime):

        try:
            company = COMPANY().filter_name(self.getOrder.order_company)
            search_channel = CHANNEL().filter_all()

            set_reason = WRR().filter_id(id=self.set_list_reasons.current.value)

            for chn in search_channel:
                if chn.name == self.getOrder.order_channel and chn.company["name"] == self.getOrder.order_company:
                    channel = {"id": chn.asanaID, "name": chn.name}

            set_carrier = CARRIER().filter_id(self.set_orderShipping_carrier.current.value)

            self.list_products = []
            for index in self.set_new_products:
                for pd in self.set_column_append_product.current.controls:
                    if pd.data == index[1]:
                        pd_qtd = pd.content.subtitle.controls[0].controls[1].value
                        pd_note = pd.content.subtitle.controls[1].controls[1].value

                product = self.getProduct[int(index[0])]

                self.list_products.append(
                    {
                        "id": product.id,
                        "produto": product.name,
                        "sku": product.sku,
                        "qtd": pd_qtd,
                        "icon": product.icon if product.icon != None or product.icon != "" else "#",
                        "personalizacao": str(pd_note).upper()
                    }
                )

            data = {
                "completion_date": shipping_date,
                "project": "arte_final",
                "custom_fields": {
                    "channel": channel["id"],
                    "company": company.asanaID,
                    "attendant": self.user_system["asanaID"],
                    "shippingMethod": set_carrier.asanaID,
                    "warranty_reason": set_reason.asana_id
                },
                "info": {
                    "number": f'GRT-{self.getOrder.order_number}' if self.getOrder.order_reference == None else f'GRT-{self.getOrder.order_reference}',
                    "customer": self.getOrder.order_customer,
                    "date": date_create.strftime('%d/%m/%Y %H:%M:%S'),
                    "channel": channel["name"],
                    "company": company.name,
                    "attendant": self.user_system["name"],
                    "address": f'{self.set_orderShipping_address.current.value}, n{self.set_orderShipping_number.current.value}, {self.set_orderShipping_complement.current.value} - {self.set_orderShipping_district.current.value}, {self.set_orderShipping_city.current.value} / {self.set_orderShipping_state.current.value}, CEP: {self.set_orderShipping_zipcode.current.value} -- Quem Recebe: {self.set_orderShipping_receiver.current.value} / Contato: {self.set_orderShipping_phone.current.value}',
                    "shippingMethod": set_carrier.name,
                    "shippingTrack": None,
                    "products": self.list_products
                },
                "comments": [
                    {"text": f'Garantia {self.getOrder.order_channel} #{self.getOrder.order_number if self.getOrder.order_reference == None else self.getOrder.order_reference}, criada por {self.user_system["name"]} | {self.app_config["app"]["name"]} v{self.app_config["app"]["version"]} - {self.app_config["app"]["build"]}', "pinned" : False}
                ],
                "warranty_reason": set_reason.reason,
                "warranty_notes": self.set_reason_notes.current.value,
                "warranty_images": self.list_image_attachment
            }

            create = TASK().create(type_body="warranty", task_data=data)
            return create


        except Exception as exc:
            print(f'\n❌ W_NEW > __save_task() ==> EXCEPTION: {exc}\n')
            self.alert.open = False
            self.page.update()
            self.clear_uploads()



    def create_order_in_magis5(self, date_create:datetime):
        """ Padroniza as informações para criar o pedido no Magis5. """

        try:
            set_order_in_magis5 = Magis5().get_orders(order_number=self.getOrder.order_number if self.getOrder.order_reference == None else self.getOrder.order_reference)
            print(f'\n🐞 W_NEW > SET_ORDER_IN_MAGIS5 ==> {set_order_in_magis5}\n')

            set_shipping = {
                '11':{"mode":"custom", "type":"SEDEX", "logistic":"34028316347219", "logistic_type":"self_service", "status":"approved", "status_payments":"approved"}, #SEDEX
                '12':{"mode":"custom", "type":"PAC", "logistic":"34028316347219", "logistic_type":"self_service", "status":"approved", "status_payments":"approved"}, #PAC
                '10':{"mode":"Pickup", "type":"retirada a combinar", "logistic":"30010432000144", "logistic_type":None, "status":"awaiting_payment", "status_payments":"approved"} #RETIRADA
            }

            set_company_channel = {
                'FBF COMUNICACAO': 'api-76bf76cf01f94a5097b8052bb7d8c856',
                'FENIX SUBLIMACAO': 'api-44339efba1f4441da237c7278ce19f94',
                'XDRI SUBLIMACAO': 'api-a7151e751e6f4d96b2f0ff1dbf243103'
            }

            list_itens_for_magis5 = list()
            total_amount = 0

            for product in set_order_in_magis5["order_items"]:
                for pdt in self.list_products:

                    if pdt["sku"] == product["item"]["seller_custom_field"]:

                        list_itens_for_magis5.append(
                            {
                                "quantity": product["quantity"],
                                "unit_price": product["unit_price"],
                                "unitMeasurement": "UN",
                                "item": {
                                    "seller_custom_field": product["item"]["seller_custom_field"],
                                    "id": product["item"]["id"],
                                    "title": product["item"]["title"],
                                    "defaultPicture": product["item"]["defaultPicture"]
                                }
                            }
                        )

                        total_amount += (product["unit_price"] * product["quantity"])

            payload_magis5 = {
                "id": f'GRT-{self.getOrder.order_number}' if self.getOrder.order_reference == None else f'GRT-{self.getOrder.order_reference}',
                "dateCreated": str(date_create.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                "quantityPackage": 1,
                "status": set_shipping[self.set_orderShipping_carrier.current.value]["status"],
                "channel": set_company_channel[self.set_orderCompany.current.value],
                "discount": 0.00,
                "erpId": "artemis5-829f955afd94438ba475a61f61089923",
                "dateApproved": str(date_create.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                "additionalNoteInvoice": "Garantia de Venda",
                "invoiceVolume": 1,
                "buyer": {
                    "last_name": '',
                    "first_name": self.set_orderShipping_receiver.current.value,
                    "full_name": self.set_orderShipping_receiver.current.value,
                    "billing_info": {
                        "doc_number": set_order_in_magis5["buyer"]["billing_info"]["doc_number"],
                        #"ie": "string"
                    },
                },
                "orderConciliation": {
                    "freight": 0.00,
                    "discount": 0.00,
                    "totalValueWithFreight": total_amount,
                    "totalValueWithoutFreight": total_amount,
                    "totalValueItem": total_amount,
                    "totalNet": total_amount
                },
                "order_items": list_itens_for_magis5,
                "payments": [
                    {
                        "status": set_shipping[self.set_orderShipping_carrier.current.value]["status_payments"],
                        "payment_type": 'UNKNOWN',
                        "installments": 1,
                        "payment_method_id": 'UNKNOWN',
                        "installment_amount": total_amount,
                        "shipping_cost": 0.00,
                        "total_paid_amount": total_amount,
                        "dueDate": str(date_create.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                        "payment_type_channel": 'UNKNOWN',
                        "payment_method_id_channel": 'UNKNOWN'
                    }
                ],
                "shipping": {
                    "created": str(date_create.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2]),
                    "shipping_mode": set_shipping[self.set_orderShipping_carrier.current.value]["mode"],
                    "shipment_type": set_shipping[self.set_orderShipping_carrier.current.value]["type"],
                    "receiver_address": {
                        "street_number": self.set_orderShipping_number.current.value,
                        "zip_code": self.set_orderShipping_zipcode.current.value,
                        "street_name": self.set_orderShipping_address.current.value,
                        "comment": self.set_orderShipping_complement.current.value,
                        "neighborhood": {"name": self.set_orderShipping_district.current.value},
                        "city": {"name": self.set_orderShipping_city.current.value},
                        "state": {"name": self.set_orderShipping_state.current.value}
                    }
                }
            }

            print(f'\n🐞 W_NEW > PAYLOAD MAGIS5 ==> {payload_magis5}\n')

            create_order = Magis5().create_order(order_json=payload_magis5)
            print(create_order)

            return True

        except Exception as exc:
            print(f'\n❌ W_NEW > create_order_in_magis5() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()
            return False



    def __sign(self):
        """ Signature String Assembly """

        sgn_order = f'GRT-{self.getOrder.order_number}' if self.getOrder.order_reference == None else f'GRT-{self.getOrder.order_reference}'
        sgn_channel = self.getOrder.order_channel
        sng_timestamp = int(time.time())*1000

        signature_factors = "{}&{}&{}".format(sgn_order, sgn_channel, sng_timestamp)
        signature_randomkey = f'FSY{random.randint(10, 99)}'

        merge_signatures = "{}{}".format(signature_factors, signature_randomkey)
        sign = f'W{base64.b64encode(merge_signatures.encode()).decode()}'
        return sign


    ## UPLOAD EVENTS ------

    def product_image_result(self, e:ft.FilePickerResultEvent):

        try:
            print(f'\n📤 W_NEW > UPLOAD PRODUCT IMAGE ==> {e.files} | {e.path}\n') ##DEBUG
            upload_list = []
            if self.product_image.result != None and self.product_image.result.files != None:
                for f in self.product_image.result.files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            f.name,
                            upload_url=self.page.get_upload_url(f'/{self.getOrder.order_number}/product/{f.name}', 600),
                        )
                    )
                self.product_image.upload(upload_list)

        except Exception as exc:
            print(f'\n❌ W_NEW > product_image_result() ==> EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()
            self.clear_uploads()


    def product_image_progress(self, e:ft.FilePickerUploadEvent):

        try:
            if e.error == None:
                if e.progress == 1.0:

                    warranty_directory = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty/{self.getOrder.order_number}")
                    warranty_product_directory = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty/{self.getOrder.order_number}/product")
                    warranty_product_attachment = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty/{self.getOrder.order_number}/product/{e.file_name}")
                    upload_directory = Path(f'D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/upload/{self.getOrder.order_number}')
                    upload_product_attachment = Path(f'D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/upload/{self.getOrder.order_number}/product/{e.file_name}')

                    if warranty_directory.exists():
                        if warranty_product_directory.exists():
                            shutil.move(src=upload_product_attachment, dst=warranty_product_directory)

                        else:
                            os.mkdir(warranty_product_directory)
                            shutil.move(src=upload_product_attachment, dst=warranty_product_directory)

                    else:
                        shutil.move(src=upload_directory, dst=f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty")

                    self.set_column_append_product.current.controls[e.control.data-1].content.leading.content.src = warranty_product_attachment
                    self.set_column_append_product.current.controls[e.control.data-1].content.leading.data["img"] = warranty_product_attachment
                    self.getProduct[e.control.data].icon = str(warranty_product_attachment)
                    self.set_product_img.current.update()

                    self.page.update()
                    self.clear_uploads()
                    return None

            else:
                print(f'\n❌ W_NEW > product_image_progress() ==> ERRO DE UPLOAD: {e.error}\n') ##DEBUG
                self.clear_uploads()
                self.snackbar.internal_error()
                self.page.update()

        except Exception as exc:
            print(f'\n❌ W_NEW > product_image_progress() ==> EXCEPTION: {exc}\n') ##DEBUG
            self.clear_uploads()
            self.snackbar.internal_error()
            self.page.update()


    def attachment_result(self, e:ft.FilePickerResultEvent):

        try:
            print(f'\n📤 W_NEW > UPLOAD ATTACHMENT IMAGE ==> {e.files} | {e.path}\n') ##DEBUG
            upload_list = []
            if self.attachment_warranty.result != None and self.attachment_warranty.result.files != None:
                for f in self.attachment_warranty.result.files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            f.name,
                            upload_url=self.page.get_upload_url(f'/{self.getOrder.order_number}/attachment/{f.name}', 600),
                        )
                    )
                self.attachment_warranty.upload(upload_list)

        except Exception as exc:
            print(f'\n❌ W_NEW > attachment_result() ==> EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()
            self.clear_uploads()


    def attachment_progress(self, e:ft.FilePickerUploadEvent):

        try:
            if e.error == None:
                if e.progress == 1.0:

                    warranty_directory = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty/{self.getOrder.order_number}")
                    warranty_attachment_directory = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty/{self.getOrder.order_number}/attachment")
                    warranty_attachment_attachment = Path(f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty/{self.getOrder.order_number}/attachment/{e.file_name}")
                    upload_directory = Path(f'D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/upload/{self.getOrder.order_number}')
                    upload_attachment_attachment = Path(f'D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/upload/{self.getOrder.order_number}/attachment/{e.file_name}')

                    if warranty_directory.exists():
                        if warranty_attachment_directory.exists():
                            if warranty_attachment_attachment.exists():
                                self.snackbar.warning("Imagem já está anexado nessa garantia.")
                                self.page.update()
                                self.clear_uploads()
                                return None

                            else:
                                shutil.move(src=upload_attachment_attachment, dst=warranty_attachment_directory)

                        else:
                            os.mkdir(warranty_attachment_directory)
                            shutil.move(src=upload_attachment_attachment, dst=warranty_attachment_directory)

                    else:
                        shutil.move(src=upload_directory, dst=f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/attachment/warranty")

                    self.list_image_attachment.append(warranty_attachment_attachment)
                    self.update_attachment(path_dir=warranty_attachment_directory)
                    self.page.update()
                    self.clear_uploads()
                    return None

            else:
                print(f'\n❌ W_NEW > attachment_progress() ==> ERRO DE UPLOAD: {e.error}\n') ##DEBUG
                self.page.update()
                self.clear_uploads()
                return None

        except Exception as exc:
            print(f'\n❌ W_NEW > attachment_progress() ==> EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()
            self.clear_uploads()
            return None

    ## ------


    def update_attachment(self, path_dir:Path) -> None:

        """ Atualiza a exibição das imagens de anexos da garantia. """

        try:
            path_directory = path_dir
            self.set_image_attachment.current.controls.clear()
            self.set_image_attachment.current.update()
            self.page.update()

            for directory, subdirectories, files in os.walk(path_directory):
                for file in files:

                    self.set_image_attachment.current.controls.append(
                        Container(
                            content=ft.Stack(
                                controls=[
                                    Image(
                                        src=self.imagem_para_base64(caminho_imagem=f'{directory}/{file}'.replace("\\", "/")),
                                        border_radius=border_radius.all(5),
                                        height=280,
                                        tooltip=file
                                    ),
                                    Container(
                                        content=IconButton(icon=icons.DELETE, bgcolor=ft.colors.with_opacity(0.8, ft.colors.OUTLINE_VARIANT), data=f'{directory}/{file}', on_click=self.delete_attachment),
                                        padding=padding.symmetric(5,5),
                                        alignment=alignment.bottom_left,
                                    )
                                ]
                            ),
                            margin=margin.symmetric(20),
                            alignment=alignment.center_left
                        )
                    )
                    self.set_image_attachment.current.update()

            self.page.update()
            return None

        except Exception as exc:
            print(f'\n❌ W_NEW > update_attachment() ==> EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()
            return None


    def delete_attachment(self, e) -> None:

        """ Excluir imagens anexos de provas da garantia. """

        try:
            file_path = Path(e.control.data.replace("\\", "/"))
            print(f'\n❌ N_NEW > delete_attachment() ==> FILE_PATH: {file_path}\n') ##DEBUG
            print(f'\n❌ N_NEW > delete_attachment() ==> LIST_ATTACHMENT: {self.list_image_attachment} | LEN LIST: {len(self.list_image_attachment)}\n') ##DEBUG

            warranty_directory = Path(f'V4/assets/attachment/warranty/{self.getOrder.order_number}')
            warranty_attachment_directory = Path(f'V4/assets/attachment/warranty/{self.getOrder.order_number}/attachment')
            warranty_product_directory = Path(f'V4/assets/attachment/warranty/{self.getOrder.order_number}/product')

            if file_path.exists():
                match len(self.list_image_attachment):
                   
                    case 1:

                        if warranty_product_directory.exists():
                            try:
                                shutil.rmtree(path=warranty_attachment_directory.resolve(), ignore_errors=True)
                            except Exception as exc:
                                print(f'\n❌ N_NEW > delete_attachment() ==> EXCEPTION DELETE 0: {exc}\n') ##DEBUG
                                self.snackbar.internal_error()
                                self.page.update()
                                return None

                        else:
                            try:
                                shutil.rmtree(path=warranty_directory.resolve(), ignore_errors=True)
                            except Exception as exc:
                                print(f'\n❌ N_NEW > delete_attachment() ==> EXCEPTION DELETE 1: {exc}\n') ##DEBUG
                                self.snackbar.internal_error()
                                self.page.update()
                                return None

                        self.list_image_attachment.remove(file_path)
                        self.set_image_attachment.current.controls.clear()
                        self.set_image_attachment.current.update()
                        self.page.update()
                        return None


                    case _:

                        try:
                            os.remove(file_path.resolve())
                            self.list_image_attachment.remove(file_path)
                            self.update_attachment(path_dir=file_path.parent)
                            self.page.update()
                            return None
                        except Exception as exc:
                            print(f'\n❌ N_NEW > delete_attachment() ==> EXCEPTION DELETE 2: {exc}\n') ##DEBUG
                            self.snackbar.internal_error()
                            self.page.update()


            else:
                print('\n❌ W_NEW > delete_attachment() ==> ERROR DELETE: ARQUIVO NÃO EXISTE NO DIRETÓRIO.\n') ##DEBUG
                if len(self.list_image_attachment) == 0:
                    self.set_image_attachment.current.controls.clear()
                    self.set_image_attachment.current.update()
                self.snackbar.not_found("Imagem não encontrada no diretório interno.")
                self.page.update()
                return None


        except Exception as exc:
            print(f'\n❌ N_NEW > delete_attachment() ==> EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()
            return None


    def clear_uploads(self) -> None:

        """ Limpa a pasta do pedido no diretório padrão de uploads. """

        try:
            path_dir = Path(f'V4/upload/{self.getOrder.order_number}')
            if path_dir.exists():
                shutil.rmtree(path=path_dir, ignore_errors=True)
            return None

        except Exception as exc:
            print(f'\n❌ W_NEW > clear_uploads() ==> EXCEPTION: {exc}\n') ##DEBUG
            return None


    def imagem_para_base64(self, caminho_imagem):
        """
        Carrega uma imagem local e a transforma em string Base64.
        """
        # 1. Verifica se o arquivo existe
        if not os.path.exists(caminho_imagem):
            print(f"Erro: Arquivo não encontrado em {caminho_imagem}")
            return None

        # 2. Determina o tipo MIME (opcional, mas recomendado)
        # Você pode precisar de uma biblioteca mais robusta para detectar o MIME
        # de forma mais confiável (como 'mimetypes'), mas para os mais comuns:
        if caminho_imagem.lower().endswith(('.png')):
            mime_type = 'image/png'
        elif caminho_imagem.lower().endswith(('.jpg', '.jpeg')):
            mime_type = 'image/jpeg'
        elif caminho_imagem.lower().endswith(('.gif')):
            mime_type = 'image/gif'
        else:
            mime_type = 'application/octet-stream' # Tipo genérico

        # 3. Abre a imagem em modo binário e lê os bytes
        with open(caminho_imagem, "rb") as arquivo_imagem:
            bytes_imagem = arquivo_imagem.read()

        # 4. Codifica os bytes em Base64
        base64_codificado = base64.b64encode(bytes_imagem).decode('utf-8')

        # 5. Cria o Data URL completo para uso no HTML
        data_url = f"data:{mime_type};base64,{base64_codificado}"

        return data_url

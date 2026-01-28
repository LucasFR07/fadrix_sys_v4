import flet as ft
import requests, base64
from datetime import datetime
from nfelib.nfe.bindings.v4_0.proc_nfe_v4_00 import NfeProc
from view.modules.magis5.magis5_get import Magis5GET
from view.component.snackbar import SnackBar_PATTERNS


class Magis5Template(Magis5GET):

    def __init__(self, order_id:str):
        super().__init__(order_id)


    def create_template(self):
        """ Cria o template para visualização pelo usuário. """

        set_content = list()
        set_order_in_magis5 = self.get_order()
        # print(f'\n🐞 ##DEBUG >> MAGIS5_TEMPLATE > create_template() == SET_TASK: {set_order_in_magis5}\n') ##DEBUG

        column_info = ft.Column(
            controls=[
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Image(src=f"assets/images/system/{set_order_in_magis5["marketplace_name"]}.png", border_radius=100, width=25),
                        title=ft.Text(value=f"PEDIDO {set_order_in_magis5["marketplace_name"]}".upper(), size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                        subtitle=ft.Text(value=set_order_in_magis5["marketplace_id"], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND)
                    ),
                    padding=ft.padding.symmetric(0,3),
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_BACKGROUND),
                    border_radius=ft.border_radius.all(7)
                ),

                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                leading=ft.Icon(name=ft.icons.NUMBERS, size=14, color=ft.colors.ON_BACKGROUND),
                                title=ft.Text(value="Magis5 ID:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                subtitle=ft.Text(value=set_order_in_magis5["magis5_id"], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                content_padding=ft.padding.all(0),
                                dense=True
                            ),
                            ft.ListTile(
                                leading=ft.Icon(name=ft.icons.TIMELINE, size=14, color=ft.colors.ON_BACKGROUND),
                                title=ft.Text(value="Magis5 Status:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                subtitle=ft.Text(value=set_order_in_magis5["magis5_status"], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                content_padding=ft.padding.all(0),
                                dense=True
                            ),
                            ft.ListTile(
                                leading=ft.Icon(name=ft.icons.PERSON_2_OUTLINED, size=14, color=ft.colors.ON_BACKGROUND),
                                title=ft.Text(value="Comprador:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                subtitle=ft.Text(value=set_order_in_magis5["buyer_name"], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                content_padding=ft.padding.all(0),
                                dense=True
                            ),
                        ],
                        spacing=0
                    ),
                    padding=ft.padding.symmetric(3,3)
                )
            ],
            col=5
        )

        link_xml = set_order_in_magis5["invoice_xml"] if len(set_order_in_magis5["invoice_xml"]) != 0 or set_order_in_magis5["invoice_xml"] != None else None

        column_expedition = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.ListTile(
                                leading=ft.Icon(name=ft.icons.NUMBERS, size=14, color=ft.colors.ON_BACKGROUND),
                                title=ft.Text(value="Número NF-e:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                subtitle=ft.Text(value=set_order_in_magis5["invoice_number"], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                trailing=ft.IconButton(icon=ft.icons.COPY_SHARP, icon_size=15, tooltip=" Copiar número para área de transferência "),
                                content_padding=ft.padding.all(0),
                                dense=True
                            ),
                            ft.ListTile(
                                leading=ft.Icon(name=ft.icons.KEY, size=14, color=ft.colors.ON_BACKGROUND),
                                title=ft.Text(value="Chave de Acesso NF-e:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                subtitle=ft.Text(value=set_order_in_magis5["invoice_key"], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                trailing=ft.IconButton(icon=ft.icons.COPY_SHARP, icon_size=15, tooltip=" Copiar chave de acesso para área de transferência "),
                                content_padding=ft.padding.all(0),
                                dense=True
                            ),
                            ft.ListTile(
                                leading=ft.Icon(name=ft.icons.LINK, size=14, color=ft.colors.ON_BACKGROUND),
                                title=ft.Text(value="XML NF-e:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                subtitle=ft.Text(spans=[ft.TextSpan(text=link_xml, style=ft.TextStyle(decoration=ft.TextDecoration.NONE, size=14, weight=ft.FontWeight.W_300, color=ft.colors.BLUE_700))], overflow=ft.TextOverflow.ELLIPSIS),
                                trailing=ft.IconButton(icon=ft.icons.DOWNLOAD, url=self.create_danfe(link_xml) if link_xml != None else None, icon_size=22, tooltip=" Baixar DANFE "),
                                content_padding=ft.padding.all(0),
                                dense=True
                            ),
                            ft.ListTile(
                                leading=ft.Icon(name=ft.icons.QR_CODE_SCANNER, size=14, color=ft.colors.ON_BACKGROUND),
                                title=ft.Text(value="Código de Rastreio:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                subtitle=ft.Text(value=set_order_in_magis5["tracking_code"], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                trailing=ft.IconButton(icon=ft.icons.COPY_SHARP, icon_size=15, tooltip=" Copiar código de rastreio para área de transferência "),
                                content_padding=ft.padding.all(0),
                                dense=True
                            ),
                        ],
                        spacing=0
                    ),
                    padding=ft.padding.symmetric(3,3)
                )
            ],
            col=5
        )

        return ft.ResponsiveRow(
            controls=[column_info, column_expedition],
            vertical_alignment=ft.CrossAxisAlignment.START,
            height=300
        )


    def create_danfe(self, link_xml:str):
        """ Cria uma visualização em PDF do xml da nota fiscal. """

        xml = requests.get(link_xml)
        nfe_proc = NfeProc.from_xml(xml.text)
        pdf_bytes = nfe_proc.to_pdf()

        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_url = f"data:application/pdf;base64,{base64_pdf}"
        return pdf_url

import flet as ft

from view.modules.tracking.tracking_get import TrackingGet
from view.component.snackbar import SnackBar_PATTERNS


class TrackingTemplate(TrackingGet):

    def __init__(self, page:ft.Page, gateway: str, company: str = None, order_number: str = None, track_number: str = None) -> None:
        super().__init__(gateway, company, order_number, track_number)

        self.page = page

        ## WIDGETS:
        self.snackbar = SnackBar_PATTERNS(self.page)
        ## ---------


    def __set_trackgin_data(self):
        """ Obbtem os dados de rastreamento. """

        try:
            return self.get_tracking_data()

        except Exception as exc:
            print(f'\n❌ TRACKING_TEMPLATE > __set_trackgin_data() == EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    def create_template(self)  -> ft.Row:
        """ Cria o template para ser exibido para os usuários. """

        try:
            set_tracking = self.__set_trackgin_data()
            print(f'\n🐞 ##DEBUG >> TRANCKING_TEMPLATE > create_template() == set_tracking: {set_tracking} | {type(set_tracking)}\n') ##DEBUG

            if len(set_tracking) == 0:
                return ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.ListTile(
                                leading=ft.Image(src=f"assets/images/system/{self.gateway}.png", border_radius=100, width=25),
                                title=ft.Text(value="GATEWAY NÃO INTEGRADO NO MOMENTO.", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND)
                            ),
                            padding=ft.padding.symmetric(0,3),
                            bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_BACKGROUND),
                            border_radius=ft.border_radius.all(7)
                        ),
                    ]
                )

            column_info = ft.Column(
                controls=[
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Image(src=f"assets/images/system/{set_tracking["tracking_gateway"]}.png", border_radius=100, width=25),
                            title=ft.Text(value="RASTREIO OBJETO", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                            subtitle=ft.Text(value=set_tracking['tracking_number'], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND)
                        ),                        
                        padding=ft.padding.symmetric(0,3),
                        bgcolor=ft.colors.with_opacity(0.1, ft.colors.ON_BACKGROUND),
                        border_radius=ft.border_radius.all(7)
                    ),

                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    leading=ft.Icon(name=ft.icons.LOCAL_SHIPPING_OUTLINED, size=14, color=ft.colors.ON_BACKGROUND),
                                    title=ft.Text(value="Tipo Logístico:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                    subtitle=ft.Text(value=set_tracking['logistics_type'], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                    content_padding=ft.padding.all(0),
                                    dense=True
                                ),
                                ft.ListTile(
                                    leading=ft.Icon(name=ft.icons.TIMELINE, size=14, color=ft.colors.ON_BACKGROUND),
                                    title=ft.Text(value="Status Logístico:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                    subtitle=ft.Text(value=set_tracking['logistics_status'], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                    content_padding=ft.padding.all(0),
                                    dense=True
                                ),
                                ft.ListTile(
                                    leading=ft.Icon(name=ft.icons.CALENDAR_MONTH_SHARP, size=14, color=ft.colors.ON_BACKGROUND),
                                    title=ft.Text(value="Previsão de Entrega:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                    subtitle=ft.Text(value=set_tracking['expected_date'], size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                    content_padding=ft.padding.all(0),
                                    dense=True
                                ),
                                # ft.ListTile(
                                #     leading=ft.Icon(name=ft.icons.ALL_OUT, size=14, color=ft.colors.ON_BACKGROUND),
                                #     title=ft.Text(value="Embalagem:", size=12, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                                #     subtitle=ft.Column(
                                #         controls=[
                                #             ft.Text(value=f'Largura: {set_tracking['package_info']['pack_width']}', size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                #             ft.Text(value=f'Altura: {set_tracking['package_info']['pack_height']}', size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                #             ft.Text(value=f'Comprimento: {set_tracking['package_info']['pack_length']}', size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                #             ft.Text(value=f'Peso: {set_tracking['package_info']['pack_weight']}', size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                #             ft.Text(value=f'Tipo: {set_tracking['package_info']['pack_shape']}', size=14, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                                #         ]
                                #     ),
                                #     content_padding=ft.padding.all(0),
                                #     dense=True
                                # ),
                            ],
                            spacing=0
                        ),
                        padding=ft.padding.symmetric(3,3)
                    )
                ],
                col=5
            )

            list_events = list()
            for event in set_tracking['tracking_events']:
                list_events.append(
                    ft.ListTile(
                        leading=ft.Icon(name=ft.icons.ARROW_RIGHT_SHARP, size=14, color=ft.colors.ON_BACKGROUND),
                        title=ft.Text(value=event['subdescription'], size=14, weight=ft.FontWeight.W_700, color=ft.colors.ON_BACKGROUND),
                        subtitle=ft.Text(value=event['description'], size=13, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                        trailing=ft.Text(value=event['update_time'], size=13, weight=ft.FontWeight.W_300, color=ft.colors.ON_BACKGROUND),
                        content_padding=ft.padding.all(0)
                    )
                )

            column_tracking = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Column(controls=list_events),
                            margin=ft.margin.only(right=15)
                        )
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.symmetric(5,5),
                col=7
            )

            return ft.ResponsiveRow(
                controls=[column_info, column_tracking],
                vertical_alignment=ft.CrossAxisAlignment.START,
                height=300
            )


        except Exception as exc:
            print(f'\n❌ TRACKING_TEMPLATE > create_template() == EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()

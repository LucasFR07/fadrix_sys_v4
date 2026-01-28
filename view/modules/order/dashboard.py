import flet as ft
from flet import ( Page, Container, Column, Row, ResponsiveRow, Text, MainAxisAlignment, CrossAxisAlignment, Icon, icons, margin, padding, alignment, border_radius, LineChart, ChartAxis, ChartAxisLabel, LineChartData, LineChartDataPoint, colors, FontWeight, BarChart, BarChartGroup, BarChartRod, DataTable, DataCell, DataColumn, DataRow, Image, ImageFit )

from view.modules.order.data_analysis import OrderAnalysis as ANLYS
from data.repository.saleschannel import SalesChannelRepository as SALES
from data.repository.order_product import OrderProductRepository as PRODUCT
from data.repository.reports import ReportsRepository as REPORT
from controllers.date_control import *

## COMPONENTES TEMPLATE
from view.component.dialog import Dialog
from view.component.snackbar import SnackBar_PATTERNS

## CONTROLES DO SISTEMA
from controllers.date_control import date_create as DATE

from copy import copy
import tablib

class OrderDashboard(Container):

    def __init__(self, page:Page, periodo:int, channel:str=None):
        super().__init__()

        self.page = page
        self.periodo = periodo if periodo != None else 60
        self.channel = channel
        self.content = self.create_content()
        self.margin = margin.symmetric(vertical=25, horizontal=25)

        self.user_system = self.page.client_storage.get("user_info")

        ## WIDGETS:
        self.snackbar = SnackBar_PATTERNS(self.page)
        self.alert = Dialog(self.page)
        ## ---------


    def create_content(self):

        content = Column(
            controls=[
                ResponsiveRow(
                    controls=[
                        Column(
                            controls=[
                                ResponsiveRow(
                                    controls=[

                                        Container(
                                            content=Row(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Container(
                                                                content=Icon(name=icons.TIMELINE, size=30, color=ft.colors.BACKGROUND),
                                                                height=50,
                                                                width=50,
                                                                bgcolor=ft.colors.ON_PRIMARY_CONTAINER,
                                                                border_radius=border_radius.all(100),
                                                                padding=padding.all(5),
                                                                margin=margin.all(0)                                                                   
                                                            )
                                                        ],
                                                        alignment=MainAxisAlignment.CENTER
                                                    ),
                                                    Column(
                                                        controls=[
                                                            Text(value="Total de Vendas", size=16, color=ft.colors.ON_BACKGROUND, weight="w500"),
                                                            Text(value=str(ANLYS(self.periodo).total_sales(self.channel)), size=24, color=ft.colors.ON_BACKGROUND, weight="w700"),
                                                            Text(value=f"Perído: {self.periodo} dias | Canal: {self.channel if self.channel != None else "Todos"}", size=12, weight="w500", color=ft.colors.ON_BACKGROUND),
                                                        ],
                                                        alignment=MainAxisAlignment.CENTER,
                                                        spacing=0,
                                                    )
                                                ],
                                                spacing=15,
                                                alignment=MainAxisAlignment.CENTER,
                                                vertical_alignment=CrossAxisAlignment.CENTER
                                            ),
                                            bgcolor=ft.colors.BACKGROUND,
                                            border_radius=border_radius.all(5),
                                            alignment=alignment.center,
                                            padding=padding.symmetric(vertical=10, horizontal=15),
                                            height=100,
                                            col=4,
                                        ),

                                        Container(
                                            content=Row(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Container(
                                                                content=Icon(name=icons.TIMELINE, size=30, color=ft.colors.BACKGROUND),
                                                                height=50,
                                                                width=50,
                                                                bgcolor=ft.colors.ON_PRIMARY_CONTAINER,
                                                                border_radius=border_radius.all(100),
                                                                padding=padding.all(5),
                                                                margin=margin.all(0)
                                                            )
                                                        ],
                                                        alignment=MainAxisAlignment.CENTER
                                                    ),
                                                    Column(
                                                        controls=[
                                                            Text(value="Total da Semana", size=16, color=ft.colors.ON_BACKGROUND, weight="w500"),
                                                            Text(value=str(ANLYS(0).total_weekSales(self.channel)), size=24, color=ft.colors.ON_BACKGROUND, weight="w700"),
                                                            Text(value=f"Perído: Semana atual | Canal: {self.channel if self.channel != None else "Todos"}", size=12, weight="w500", color=ft.colors.ON_BACKGROUND),                                                    
                                                        ],
                                                        alignment=MainAxisAlignment.CENTER,
                                                        spacing=0,
                                                    )
                                                ],
                                                spacing=15,
                                                alignment=MainAxisAlignment.CENTER,
                                                vertical_alignment=CrossAxisAlignment.CENTER
                                            ),
                                            bgcolor=ft.colors.BACKGROUND,
                                            border_radius=border_radius.all(5),
                                            alignment=alignment.center,
                                            padding=padding.symmetric(vertical=10, horizontal=15),
                                            height=100,
                                            col=4,
                                        ),  

                                        Container(
                                            content=Row(
                                                controls=[
                                                    Column(
                                                        controls=[
                                                            Container(
                                                                content=Icon(name=icons.TIMELINE, size=30, color=ft.colors.BACKGROUND),
                                                                height=50,
                                                                width=50,
                                                                bgcolor=ft.colors.ON_PRIMARY_CONTAINER,
                                                                border_radius=border_radius.all(100),
                                                                padding=padding.all(5),
                                                                margin=margin.all(0)                                                                   
                                                            )
                                                        ],
                                                        alignment=MainAxisAlignment.CENTER
                                                    ),
                                                    Column(
                                                        controls=[
                                                            Text(value="Envios do Dia", size=16, color=ft.colors.ON_BACKGROUND, weight="w500"),
                                                            Text(value=str(ANLYS(0).total_shippingDay(self.channel)), size=24, color=ft.colors.ON_BACKGROUND, weight="w700"),
                                                            Text(value=f"Perído: Hoje | Canal: {self.channel if self.channel != None else "Todos"}", size=12, weight="w500", color=ft.colors.ON_BACKGROUND),                                                    
                                                        ],
                                                        alignment=MainAxisAlignment.CENTER,
                                                        spacing=0,
                                                    )
                                                ],
                                                spacing=15,
                                                alignment=MainAxisAlignment.CENTER,
                                                vertical_alignment=CrossAxisAlignment.CENTER
                                            ),
                                            bgcolor=ft.colors.BACKGROUND,
                                            border_radius=border_radius.all(5),
                                            alignment=alignment.center,
                                            padding=padding.symmetric(vertical=10, horizontal=15),
                                            height=100,
                                            col=4,
                                        ),                                                                                      

                                    ]
                                ),

                                ResponsiveRow(
                                    controls=[
                                        Container(
                                            content=self.evolucao_canal(),
                                            bgcolor=ft.colors.BACKGROUND,
                                            padding=padding.symmetric(vertical=15, horizontal=20),
                                            margin=margin.symmetric(vertical=5),
                                            border_radius=border_radius.all(5),
                                            col=7
                                        ),
                                        Container(
                                            content=self.total_canal(),
                                            bgcolor=ft.colors.BACKGROUND,
                                            padding=padding.symmetric(vertical=15, horizontal=20),
                                            margin=margin.symmetric(vertical=5),
                                            border_radius=border_radius.all(5),
                                            col=5
                                        )
                                    ]
                                ),

                                ResponsiveRow(
                                    controls=[
                                        Container(
                                            content=self.rank_produtos(),
                                            bgcolor=ft.colors.BACKGROUND,
                                            padding=padding.symmetric(vertical=15, horizontal=20),
                                            margin=margin.symmetric(vertical=5),
                                            border_radius=border_radius.all(5),
                                            col=7
                                        ),
                                        Container(
                                            content=self.rank_byers(),
                                            bgcolor=ft.colors.BACKGROUND,
                                            padding=padding.symmetric(vertical=15, horizontal=20),
                                            margin=margin.symmetric(vertical=5),
                                            border_radius=border_radius.all(5),
                                            col=5
                                        ),
                                    ]
                                ),

                                ResponsiveRow(
                                    controls=[
                                        Container(
                                            content=self.total_usuario(),
                                            bgcolor=ft.colors.BACKGROUND,
                                            padding=padding.symmetric(vertical=15, horizontal=20),
                                            margin=margin.symmetric(vertical=5),
                                            border_radius=border_radius.all(5),
                                            col=7
                                        )
                                    ]
                                ),
                            ],
                            col=12
                        ),
                    ],
                )
            ],
            scroll="hidden"
        )

        return content
    

    def evolucao_canal(self):

        query = ANLYS(self.periodo).evolution_by_channel(self.channel)
        query_dates = date_subtractdaysCALC(self.periodo+1)
        query_dates.reverse()
        query_channel = SALES().filter_all()

        data_list = list()
        label_list = list()
        temp_list = list()
        calc_max = 0
        set_channel = {x.name for x in query_channel}
        colors_dict = {'Amazon': colors.GREY_900, 'Americanas': colors.RED_ACCENT_700, 'Magazine Luiza': colors.BLUE_900, 'Mercado Livre': colors.YELLOW_800, 'Shopee': colors.DEEP_ORANGE_ACCENT_400, 'Prestashop': colors.DEEP_PURPLE_500, 'Shein': colors.INDIGO_600, 'TikTok': colors.GREY_900}

        for channel in set_channel:
            for x, y in query.iterrows():
                if x[0] == channel:
                    calc_max = y.values[0] if y.values[0] > calc_max else calc_max
                    temp_list.append(
                        LineChartDataPoint(
                            x=query_dates.index(x[1]),
                            y=y.values[0],
                            show_tooltip=True,
                            tooltip=f'{channel}: {y.values[0]}',
                            tooltip_align=alignment.center_left,
                            point=True
                        )
                    )
                else:
                    continue

            if len(temp_list) == 0:
                continue
            else:
                data_list.append(
                    LineChartData(
                        data_points=copy(temp_list),
                        color=colors_dict[channel],
                        curved=True,
                        stroke_width=4.5,
                        visible=True,
                        stroke_cap_round=False
                    )
                )
                temp_list.clear()

        for x in range(0,len(query_dates),2):
            label_list.append(
                ChartAxisLabel(
                    value=int(query_dates.index(query_dates[x])),
                    label=Text(f'{query_dates[x].day:02}/{query_dates[x].month}', size=14, weight="w500")
                ),
            )

        chart = LineChart(
            data_series=data_list,
            top_axis=ChartAxis(
                title=Text(f"💹 Evolução das Vendas (Marketplace)", size=16, weight="w500", color=ft.colors.ON_BACKGROUND),
                title_size=24,
                show_labels=False
            ),
            right_axis=ChartAxis(
                title=Text("", size=20, weight="w500", color=ft.colors.ON_BACKGROUND),
                title_size=50,
                show_labels=False
            ),            
            left_axis=ChartAxis(
                labels=[
                    ChartAxisLabel(
                        value=10,
                        label=Text("10", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=25,
                        label=Text("25", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=50,
                        label=Text("50", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=80,
                        label=Text("80", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=100,
                        label=Text("100", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=150,
                        label=Text("150", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=200,
                        label=Text("200", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=300,
                        label=Text("300", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                    ChartAxisLabel(
                        value=400,
                        label=Text("400", size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND),
                    ),
                ],
                labels_size=40,
            ),
            bottom_axis=ChartAxis(
                labels=label_list,
                labels_size=28,
            ),
            tooltip_bgcolor=colors.with_opacity(0.9, ft.colors.OUTLINE),
            min_x=0,
            max_y=calc_max*2,
            min_y=0,
            animate=5000,
            horizontal_grid_lines=ft.ChartGridLines(color=ft.colors.with_opacity(0.3, ft.colors.ON_BACKGROUND), width=0.3),
            height=400,
            expand=True,
        )

        return chart


    def total_canal(self):

        query = ANLYS(self.periodo).total_by_channel(self.channel)
        bar_groups = list()
        bottom_axis = list()
        index = 0
        calc_max = 0

        colors_dict = {'Amazon': colors.GREY_900, 'Americanas': colors.RED_ACCENT_700, 'Magazine Luiza': colors.BLUE_900, 'Mercado Livre': colors.YELLOW_800, 'Shopee': colors.DEEP_ORANGE_ACCENT_400, 'Prestashop': colors.DEEP_PURPLE_500, 'Shein': colors.INDIGO_600, 'TikTok': colors.GREY_900}

        for x, y in query.iterrows():
            calc_max = y[0] if y[0] > calc_max else calc_max
            bar_groups.append(
                BarChartGroup(
                    x=index,
                    bar_rods=[
                        BarChartRod(
                            from_y=0,
                            to_y=y[0],
                            width=30,
                            color=colors_dict[x[0]],
                            tooltip=f'{y[0]} vendas',
                            tooltip_style=ft.TextStyle(color=ft.colors.BACKGROUND, weight=ft.FontWeight.W_600),
                            border_radius=0
                        ),
                    ],
                )
            )

            bottom_axis.append(
                ChartAxisLabel(
                    value=index, 
                    label=Container(
                        content=Text(value=f'{x[0]}\n{x[1].split()[0]}', size=10, weight="w400", text_align=ft.TextAlign.CENTER),
                        padding=ft.padding.symmetric(10, 5)
                    )
                )
            )
            index+=1


        chart = BarChart(
            bar_groups=bar_groups,
            top_axis=ChartAxis(
                title=Text(f"💹 Total de Vendas (Canal/Empresa)", size=16, weight="w500", color=ft.colors.ON_BACKGROUND),
                title_size=24,
                show_labels=False
            ),
            bottom_axis=ChartAxis(
                labels=bottom_axis,
                labels_size=60,
            ),
            tooltip_bgcolor=colors.with_opacity(0.9, ft.colors.OUTLINE),
            max_y=int(calc_max*1.5),
            interactive=True,
            expand=True,
        )

        return chart


    def rank_produtos(self):

        rank = ANLYS(self.periodo).moda_product(self.channel)
        list_cells = list()
        rank_order = 1

        xls_hearder = ["Rank", "Produto", "SKU", "Qtd. Vendas"]
        xls_data = list()        

        for x, y in rank.iterrows():
            product = PRODUCT().filter_sku(x)
            list_cells.append(
                DataRow(
                    cells=[
                        DataCell(content=Text(f'{rank_order}º', weight="w600", color=ft.colors.ON_BACKGROUND)),
                        DataCell(content=Image(src=product.icon, width=40, fit=ImageFit.FILL)),
                        DataCell(content=Text(product.name, color=ft.colors.ON_BACKGROUND, selectable=True)),
                        DataCell(content=Text(product.sku, color=ft.colors.ON_BACKGROUND, selectable=True)),
                        DataCell(content=Text(f'{int(y[0])} vendas', color=ft.colors.ON_BACKGROUND)),
                    ]
                )
            )

            xls_data.append((f'{rank_order}º', product.name, product.sku, int(y[0])))
            rank_order+=1

        self.product_table = DataTable(
            width=2600,
            column_spacing=20,
            vertical_lines=None,
            data_row_color={"hovered": ft.colors.SECONDARY_CONTAINER},
            # data_row_height=60,
            divider_thickness=0,
            heading_row_color= ft.colors.ON_PRIMARY_CONTAINER,
            heading_row_height=30,
            show_bottom_border=True,
            sort_ascending=False,
            sort_column_index=0,
            columns=[
                DataColumn(Text("Rank", color=ft.colors.BACKGROUND, visible=False)),
                DataColumn(Text("", visible=False, color=ft.colors.BACKGROUND)),
                DataColumn(Text("Produto", color=ft.colors.BACKGROUND, visible=False)),
                DataColumn(Text("SKU", color=ft.colors.BACKGROUND, visible=False)),
                DataColumn(Text("Qtd.", color=ft.colors.BACKGROUND, visible=False)),
            ],
            rows=list_cells
        )

        return Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(f"🏆 Rank Produtos Mais Vendidos", size=16, weight="w500", color=ft.colors.ON_BACKGROUND),
                            ft.IconButton(icon=icons.DOWNLOAD, icon_color=ft.colors.ON_BACKGROUND, data=["rank_products", xls_hearder, xls_data], on_click=self.__report)
                        ],
                        alignment=MainAxisAlignment.CENTER
                    ),
                    
                    self.product_table
                ],
                scroll="hidden",
                spacing=15,
                horizontal_alignment=CrossAxisAlignment.CENTER
            ),
            bgcolor=ft.colors.BACKGROUND,
            padding=padding.symmetric(15,20),
            height=300
        )


    def rank_byers(self):

        rank = ANLYS(self.periodo).moda_buyer(self.channel)
        list_cells = list()
        rank_order = 1

        for x, y in rank.iterrows():
            list_cells.append(
                DataRow(
                    cells=[
                        DataCell(content=Text(f'{rank_order}º', weight="w600", color=ft.colors.ON_BACKGROUND)),
                        DataCell(content=Text(x, color=ft.colors.ON_BACKGROUND, selectable=True)),
                        DataCell(content=Text(f'{int(y[0])} vendas', color=ft.colors.ON_BACKGROUND)),
                    ]
                )
            )
            rank_order+=1

        self.buyer_table = DataTable(
            width=2600,
            column_spacing=20,
            vertical_lines=None,
            data_row_color={"hovered": ft.colors.SECONDARY_CONTAINER},
            divider_thickness=0,
            heading_row_color= ft.colors.ON_PRIMARY_CONTAINER,
            heading_row_height=30,
            show_bottom_border=True,
            sort_ascending=False,
            sort_column_index=0,
            columns=[
                DataColumn(Text("Rank", color=ft.colors.BACKGROUND, visible=False)),
                DataColumn(Text("Cliente", color=ft.colors.BACKGROUND, visible=False)),
                DataColumn(Text("Qtd.", color=ft.colors.BACKGROUND, visible=False)),
            ],
            rows=list_cells
        )

        return Container(
            content=Column(
                controls=[
                    Text(f"🏆 Rank Melhores Clientes", size=16, weight="w500", color=ft.colors.ON_BACKGROUND),
                    self.buyer_table
                ],
                scroll="hidden",
                spacing=15,
                horizontal_alignment=CrossAxisAlignment.CENTER
            ),
            bgcolor=ft.colors.BACKGROUND,
            padding=padding.symmetric(15,20),
            height=300
        )


    def total_usuario(self):

        query = ANLYS(self.periodo).total_by_user(self.channel)
        data_series = list()
        left_axis = list()
        right_axis = list()
        botton_axis = list()
        index_user = 5
        calc_max = 0

        for x, y in query.iterrows():
            calc_max +=1
            data_series.append(
                LineChartData(
                    data_points=[
                        LineChartDataPoint(
                            x=0,
                            y=index_user,
                            show_tooltip=False,
                            point=False
                        ),
                        LineChartDataPoint(
                            x=y[0],
                            y=index_user,
                            show_tooltip=False,
                            point=False
                        )
                    ],
                    color=ft.colors.ON_PRIMARY_CONTAINER,
                    curved=True,
                    stroke_width=25,
                    visible=True,
                    stroke_cap_round=False,
                    point=False
                )
            )

            left_axis.append(ChartAxisLabel(value=index_user, label=Text(x, size=14, weight=FontWeight.BOLD, color=ft.colors.ON_BACKGROUND)))
            right_axis.append(ChartAxisLabel(value=index_user, label=Text(f'   {y[0]} vendas', size=14, color=ft.colors.ON_BACKGROUND)))
            botton_axis.append(ChartAxisLabel(value=int(y[0])))
            index_user+=5

        chart = LineChart(
            data_series=data_series,
            top_axis=ChartAxis(
                title=Text(f"💹 Total de Vendas (Usuário)", size=16, weight="w500", color=ft.colors.ON_BACKGROUND),
                title_size=24,
                show_labels=False
            ),
            right_axis=ChartAxis(
                labels=right_axis,
                labels_size=130,
            ),
            bottom_axis=ChartAxis(
                labels=botton_axis,
                labels_size=28,
                visible=False
            ),
            left_axis=ChartAxis(
                labels=left_axis,
                labels_size=130,
            ),            
            min_y=0,
            max_y=calc_max*6,
            expand=True,
            interactive=False
        )

        return chart


    def __report(self, e):

        try:
            report_type:str = e.control.data[0]
            header:list = e.control.data[1]
            data:list = e.control.data[2]
            report_date:datetime = DATE()

            path_directory = f"D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/report/{report_type}"
            title = f'FSYS_{report_type.replace("_", "")}__{self.channel if self.channel != None else "GERAL"}_{report_date.strftime('%Y-%m-%d %H.%M.%S')}'.upper()

            excel = tablib.Dataset(*data, headers=header)
            excel.title = f'{report_type.replace("_", " ")} _ {self.channel if self.channel != None else "GERAL"} _ LAST {self.periodo}D'.upper()

            with open(f'{path_directory}/{title}.xlsx', 'wb') as f:
                f.write(excel.export('xlsx'))

            print(f'\n⬇ DOWNLOAD REPORT >> {title}\n')
            self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx')

            REPORT().insert(
                report_date=report_date,
                report_user=self.user_system["name"],
                report_type=report_type,
                report_title=title,
                report_file_extension='.xlsx',
                report_path=f'{path_directory}/{title}.xlsx'
            )

            self.snackbar.download(event=lambda e: self.page.launch_url(url=f'http://192.168.1.35:62024/{path_directory}/{title}.xlsx'))
            self.page.update()

        except Exception as exc:
            print(f'\n❌ DASHBOARD_ORDER > __report() ==> EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()

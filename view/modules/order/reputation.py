import flet as ft
from flet import ( Page, Container, Column, Row, ResponsiveRow, Text, MainAxisAlignment, CrossAxisAlignment, Icon, icons, margin, padding, alignment, border_radius, colors, FontWeight, DataTable, DataCell, DataColumn, DataRow, Image )

from data.repository.saleschannel import SalesChannelRepository as SALES

from controllers.date_control import *

from source.api.meliApi import MercadoLivre as MELI
from source.api.shopeeApi import Shopee as SHOPEE


class ReputationDashboard(Container):

    def __init__(self, page:Page):
        super().__init__()

        self.page = page
        self.content = self.create_content()
        self.margin = margin.symmetric(vertical=25, horizontal=25)


    def create_content(self):

        list_channels = list()
        get_channels = SALES().filter_all()

        for channel in get_channels:
            company = str(channel.company["name"]).split()

            match channel.name:

                case "Shein" | "Magazine Luiza" | "Amazon" | "Americanas" | "Prestashop":
                    print(f'\n❌ CANAL {channel.name.upper()} - SEM REPUTAÇÃO DISPONÍVEL PELA API.\n')

                case _:
                    set_reputation = self.get_reputation(channel=channel.name, company=channel.company["name"])

                    if set_reputation == None:
                        print(f'\n❌ ERRO AO OBTER REPUTAÇÃO => CONTA {channel.name} ({channel.company["name"]})\n')

                    else:
                        list_channels.append(
                            Container(
                                content=Column(
                                    controls=[
                                        Container(
                                            content=Row(
                                                controls=[
                                                    Image(width=22, src=channel.icon),
                                                    Text(f'{channel.name} ({company[0]})'.upper(), size=15, weight=FontWeight.W_700, color=ft.colors.ON_BACKGROUND)
                                                ],
                                                alignment=MainAxisAlignment.CENTER
                                            ),
                                            bgcolor=ft.colors.PRIMARY_CONTAINER,
                                            border_radius=border_radius.all(5),
                                            padding=padding.symmetric(10,20),
                                        ),
                                        Container(
                                            content=set_reputation,
                                            padding=padding.symmetric(10,20),
                                        )
                                    ]
                                ),
                                bgcolor=ft.colors.BACKGROUND,
                                padding=padding.symmetric(vertical=15, horizontal=20),
                                margin=margin.symmetric(vertical=5),
                                border_radius=border_radius.all(5),
                                col=4
                            ),
                        )

        return Column(
            controls=[ResponsiveRow(controls=list_channels)],
            scroll="hidden"
        )


    def performance_color(self, color_num:str=None):

        performance = {
            "5": {"color": "#F23D4F", "shopee_text": ""},
            "4": {"color": "#FFB657", "shopee_text": "Ruim"},
            "3": {"color": "#FEF211", "shopee_text": "Melhorias Necessárias"},
            "2": {"color": "#AEEF1B", "shopee_text": "Bom"},
            "1": {"color": "#00A650", "shopee_text": "Excelente"},
        }

        return [Container(width=42, height=10, bgcolor=value["color"], opacity=0.2 if color_num != keys else None) for keys, value in performance.items()]


    def get_reputation(self, channel:str, company:str):

        match channel:
            
            case "Mercado Livre":
                try:
                    reputation_meli = MELI(company).seller_reputation()
                    # print(f'\nreputation.py > get_reputation() ==> {reputation_meli}\n') #DEBUG
                    questions_meli = MELI(company).questions_response_time()
                    # print(f'\nreputation.py > get_reputation() ==> {questions_meli}\n') #DEBUG
                    color_reference = ["5", "4", "3", "2", "1"]

                    ##INFO REPUTATION
                    color_reputation = reputation_meli["seller_reputation"]["level_id"]
                    seller_reputation = reputation_meli["seller_reputation"]["power_seller_status"]

                    claims_rate = reputation_meli["seller_reputation"]["metrics"]["claims"]["rate"]
                    claims_value = reputation_meli["seller_reputation"]["metrics"]["claims"]["value"]

                    cancellations_rate = reputation_meli["seller_reputation"]["metrics"]["cancellations"]["rate"]
                    cancellations_value = reputation_meli["seller_reputation"]["metrics"]["cancellations"]["value"]

                    delayed_handling_time_rate = reputation_meli["seller_reputation"]["metrics"]["delayed_handling_time"]["rate"]
                    delayed_handling_time_value = reputation_meli["seller_reputation"]["metrics"]["delayed_handling_time"]["value"]

                    weekdays_working_hours = questions_meli["weekdays_working_hours"]["response_time"] if questions_meli["weekdays_working_hours"]["response_time"] != None else 0
                    weekdays_extra_hours = questions_meli["weekdays_extra_hours"]["response_time"] if questions_meli["weekdays_extra_hours"]["response_time"] != None else 0
                    weekend = questions_meli["weekend"]["response_time"] if questions_meli["weekend"]["response_time"] != None else 0

                    return Column(

                        controls=[

                            Row(
                                controls=[
                                    Icon(name=icons.VERIFIED if seller_reputation != None else icons.ERROR_OUTLINE, size=18, color=ft.colors.ON_BACKGROUND),
                                    Text(f'MercadoLíder {seller_reputation}'.upper() if seller_reputation != None else "SEM REPUTAÇÃO", size=14, weight="w500", color=ft.colors.ON_BACKGROUND)
                                ],
                                spacing=2,
                                alignment=MainAxisAlignment.CENTER
                            ),

                            Row(
                                controls=self.performance_color(color_reference[int(color_reputation.split("_")[0])-1]) if color_reputation != None else self.performance_color(),
                                spacing=3,
                                alignment=MainAxisAlignment.CENTER
                            ),

                            ResponsiveRow(
                                controls=[
                                    Container(
                                        content=Column(
                                            controls=[
                                                Text('Reclamações'.upper(), weight=FontWeight.W_600, size=10),
                                                Text(f'{round(claims_rate*100, 2)}%', weight=FontWeight.W_600, size=18, color="#00A650" if claims_rate*100 <= claims_value else "#FFB657", tooltip=f'{claims_value} Vendas Afetadas'),
                                            ],
                                            horizontal_alignment=CrossAxisAlignment.CENTER,
                                            spacing=3
                                        ),
                                        margin=margin.only(top=10),
                                        col=4
                                    ),
                                    Container(
                                        content=Column(
                                            controls=[
                                                Text('Cancelamentos'.upper(), weight=FontWeight.W_600, size=10),
                                                Text(f'{round(cancellations_rate*100, 2)}%', weight=FontWeight.W_600, size=18, color="#00A650" if cancellations_rate <= cancellations_value else "#FFB657", tooltip=f'{cancellations_value} Vendas Afetadas'),
                                            ],
                                            horizontal_alignment=CrossAxisAlignment.CENTER,
                                            spacing=3
                                        ),
                                        margin=margin.only(top=10),
                                        col=4
                                    ),
                                    Container(
                                        content=Column(
                                            controls=[
                                                Text('Atrasos'.upper(), weight=FontWeight.W_600, size=10),
                                                Text(f'{round(delayed_handling_time_rate*100, 2)}%', weight=FontWeight.W_600, size=18, color="#00A650", tooltip=f'{delayed_handling_time_value} Vendas Afetadas'),
                                            ],
                                            horizontal_alignment=CrossAxisAlignment.CENTER,
                                            spacing=3
                                        ),
                                        margin=margin.only(top=10),
                                        col=4
                                    ),
                                ],
                                alignment=MainAxisAlignment.CENTER,                                        
                            ),

                            ft.Divider(color=colors.OUTLINE, opacity=0.3),

                            Column(
                                controls=[

                                    Container(
                                        content=Text(value="TEMPO DE RESPOSTA PERGUNTAS", size=13, weight=FontWeight.W_700, color=colors.ON_BACKGROUND),
                                        padding=padding.only(bottom=15),
                                        alignment=alignment.center
                                    ),

                                    ResponsiveRow(
                                        controls=[

                                            Container(
                                                content=Column(
                                                    controls=[
                                                        Text(value="EXPEDIENTE", size=10, color=colors.ON_BACKGROUND, weight=FontWeight.W_600),

                                                        Text(value=f'{weekdays_working_hours}m' if int(weekdays_working_hours) < 60 else f'{int(int(weekdays_working_hours)/60)}hs', size=18, weight=FontWeight.W_600, color="#00A650" if int(weekdays_working_hours) < 60 else colors.ERROR, tooltip="Período: Segunda a sexta das 9 às 18 h / Recomendado: -1h")
                                                    ],
                                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                                    spacing=3
                                                ),
                                                col=4
                                            ),

                                            Container(
                                                content=Column(
                                                    controls=[
                                                        Text(value="EXTRA", size=10, color=colors.ON_BACKGROUND, weight=FontWeight.W_600),

                                                        Text(value=f'{weekdays_extra_hours}m' if int(weekdays_extra_hours) < 60 else f'{int(int(weekdays_extra_hours)/60)}hs', size=18, weight=FontWeight.W_600, color="#00A650" if int(weekdays_extra_hours) < 60 else colors.ERROR, tooltip="Período: Segunda a sexta das 18 às 00 h / Recomendado: -1h")
                                                    ],
                                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                                    spacing=3
                                                ),
                                                col=4
                                            ),

                                            Container(
                                                content=Column(
                                                    controls=[
                                                        Text(value="SAB/DOM", size=10, color=colors.ON_BACKGROUND, weight=FontWeight.W_600),

                                                        Text(value=f'{weekend}m' if int(weekend) < 60 else f'{int(int(weekend)/60)}hs', size=18, weight=FontWeight.W_600, color="#00A650" if int(weekend) < 60 else colors.ERROR, tooltip="Período: Sábados e domingos / Recomendado: -1h")
                                                    ],
                                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                                    spacing=3
                                                ),
                                                col=4
                                            ),

                                        ],
                                        alignment=MainAxisAlignment.CENTER
                                    )

                                ],
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                                spacing=2
                            ),

                            ft.Divider(color=colors.OUTLINE, opacity=0.3),

                            Column(
                                controls=[

                                    Container(
                                        content=Text(value="AVALIAÇÃO CLIENTES", size=13, weight=FontWeight.W_700, color=colors.ON_BACKGROUND),
                                        padding=padding.only(bottom=15),
                                        alignment=alignment.center
                                    ),

                                    ResponsiveRow(
                                        controls=[
                                            Container(
                                                content=Column(
                                                    controls=[
                                                        Text(value="NEGATIVA", size=10, color=colors.ON_BACKGROUND, weight=FontWeight.W_600),
                                                        Text(value=f'😡{reputation_meli["seller_reputation"]["transactions"]["ratings"]["negative"]*100} %', size=16, weight=FontWeight.W_700, color=colors.ON_BACKGROUND)
                                                    ],
                                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                                    spacing=3
                                                ),
                                                col=4
                                            ),
                                            Container(
                                                content=Column(
                                                    controls=[
                                                        Text(value="NEUTRA", size=10, color=colors.ON_BACKGROUND, weight=FontWeight.W_600),
                                                        Text(value=f'😐{reputation_meli["seller_reputation"]["transactions"]["ratings"]["neutral"]*100} %', size=16, weight=FontWeight.W_700, color=colors.ON_BACKGROUND)
                                                    ],
                                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                                    spacing=3                                                
                                                ),
                                                col=4
                                            ),
                                            Container(
                                                content=Column(
                                                    controls=[
                                                        Text(value="POSITIVA", size=10, color=colors.ON_BACKGROUND, weight=FontWeight.W_600),
                                                        Text(value=f'😃{reputation_meli["seller_reputation"]["transactions"]["ratings"]["positive"]*100}%', size=18, weight=FontWeight.W_700, color=colors.ON_BACKGROUND)
                                                    ],
                                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                                    spacing=3
                                                ),
                                                col=4
                                            ),
                                        ],
                                        alignment=MainAxisAlignment.CENTER
                                    )
                                ],
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                                spacing=2
                            ),

                            ft.Divider(color=colors.OUTLINE, opacity=0.3),

                            Column(
                                controls=[

                                    Container(
                                        content=Text(value="INFORMAÇÕES DA CONTA", size=13, weight=FontWeight.W_700, color=colors.ON_BACKGROUND),
                                        padding=padding.only(bottom=7),
                                        alignment=alignment.center
                                    ),

                                    Row(
                                        controls=[
                                            # Row(controls=[Icon(name=icons.PERM_IDENTITY, size=12, color=colors.ON_BACKGROUND), Text(value="ID: ", weight=ft.FontWeight.W_600, size=12, color=colors.ON_BACKGROUND), Text(value=reputation_meli["id"], size=12, color=colors.ON_BACKGROUND)], spacing=1),

                                            Row(controls=[Icon(name=icons.PERM_IDENTITY, size=12, color=colors.ON_BACKGROUND), Text(value="NOME: ", weight=ft.FontWeight.W_600, size=12, color=colors.ON_BACKGROUND), Text(value=reputation_meli["nickname"], size=12, color=colors.ON_BACKGROUND)], spacing=1),

                                            Row(controls=[Icon(name=icons.LINK_OUTLINED, size=12, color=colors.ON_BACKGROUND), Text(value="LOJA : ", weight=ft.FontWeight.W_600, size=12, color=colors.ON_BACKGROUND), Text(spans=[ft.TextSpan(text="VER", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE), url=reputation_meli["permalink"])])], spacing=1),
                                        ],
                                        spacing=10,
                                        alignment=MainAxisAlignment.CENTER
                                    ),

                                ],
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                                spacing=2
                            ),

                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER
                    )

                except Exception as exc:
                    print(f'\n❌ REPUTATION > get_reputation() ==> EXCEPTION IN MERCADO LIVRE {company}: {exc}\n')
                    return None
                    # return Column(
                    #     controls=[
                    #         Container(
                    #             content=Text(value="❌ ERRO AO CONSULTAR"),
                    #             padding=padding.symmetric(10),
                    #             alignment=alignment.center
                    #         )
                    #     ],
                    #     horizontal_alignment=CrossAxisAlignment.CENTER
                    # )                    

            case "Shopee":
                try:
                    reputation_shopee = SHOPEE(company).shop_performance()
                    # print(f'reputations.py > get_reputation() ==> {reputation_shopee}') #DEBUG
                    penalty_shopee = SHOPEE(company).shop_penalty()
                    # print(f'reputations.py > get_reputation() ==> {penalty_shopee}') #DEBUG

                    penalty = penalty_shopee["response"]["penalty_points"]["overall_penalty_points"]
                    color_reputation = str(reputation_shopee["response"]["overall_performance"])
                    performance_name = {"5": "", "4": "Ruim", "3": "Melhorias Necessárias", "2": "Bom", "1": "Excelente"}                

                    return Column(
                        controls=[

                            Row(
                                controls=[
                                    Icon(name=icons.VERIFIED, size=18, color=ft.colors.ON_BACKGROUND),
                                    Text(str(performance_name[color_reputation]).upper(), size=14, weight="w500", color=ft.colors.ON_BACKGROUND)
                                ],
                                spacing=2,
                                alignment=MainAxisAlignment.CENTER
                            ),

                            Row(
                                controls=self.performance_color(color_reputation),
                                spacing=3,
                                alignment=MainAxisAlignment.CENTER
                            ),

                            ResponsiveRow(
                                controls=[

                                    Container(
                                        content=Column(
                                            controls=[
                                                Text('Satisfação'.upper(), weight=FontWeight.W_600, size=10),
                                                Text(
                                                    value=f'{reputation_shopee["response"]["customer_satisfaction"]["overall_reviewing_rate"]["total_data"]["my_shop_performance"]}'.replace("/5", "%"),
                                                    weight=FontWeight.W_600,
                                                    size=18,
                                                    color="#00A650" if reputation_shopee["response"]["customer_satisfaction"]["overall_reviewing_rate"]["total_data"]["my_shop_performance"] != None and float(reputation_shopee["response"]["customer_satisfaction"]["overall_reviewing_rate"]["total_data"]["my_shop_performance"].replace("/5", "")) >= float(reputation_shopee["response"]["customer_satisfaction"]["overall_reviewing_rate"]["total_data"]["target"].replace(">=", "").replace("/5", "")) else colors.ERROR,
                                                    tooltip=f'Métrica de Satisfação do cliente. Meta da loja: {reputation_shopee["response"]["customer_satisfaction"]["overall_reviewing_rate"]["total_data"]["target"].replace("/5", "%")}'
                                                ),
                                            ],
                                            horizontal_alignment=CrossAxisAlignment.CENTER,
                                            spacing=3
                                        ),
                                        margin=margin.only(top=10),
                                        col=4
                                    ),

                                    Container(
                                        content=Column(
                                            controls=[
                                                Text('Resposta'.upper(), weight=FontWeight.W_600, size=10),
                                                Text(
                                                    value=f'{reputation_shopee["response"]["customer_service"]["response_rate"]["total_data"]["my_shop_performance"]}',
                                                    weight=FontWeight.W_600,
                                                    size=18,
                                                    color="#00A650" if float(reputation_shopee["response"]["customer_service"]["response_rate"]["total_data"]["my_shop_performance"].replace("%", "")) >= float(reputation_shopee["response"]["customer_service"]["response_rate"]["total_data"]["target"].replace(">=", "").replace("%", "")) else colors.ERROR,
                                                    tooltip=f'Métrica de taxa de Resposta. Meta da loja: {reputation_shopee["response"]["customer_service"]["response_rate"]["total_data"]["target"]}'
                                                ),
                                            ],
                                            horizontal_alignment=CrossAxisAlignment.CENTER,
                                            spacing=3
                                        ),
                                        margin=margin.only(top=10),
                                        col=4
                                    ),

                                    Container(
                                        content=Column(
                                            controls=[
                                                Text('Penalidades'.upper(), weight=FontWeight.W_600, size=10),
                                                Text(
                                                    value=penalty,
                                                    weight=FontWeight.W_600,
                                                    size=18,
                                                    color="#00A650" if penalty == 0 else colors.ERROR,
                                                    tooltip=f'Métrica de pontos de penalidade da loja.'
                                                ),
                                            ],
                                            horizontal_alignment=CrossAxisAlignment.CENTER,
                                            spacing=3
                                        ),
                                        margin=margin.only(top=10),
                                        col=4
                                    ),

                                ],
                                alignment=MainAxisAlignment.CENTER,                                        
                            ),

                            ft.Divider(color=colors.OUTLINE, opacity=0.3),

                            ft.Tabs(
                                selected_index=0,
                                animation_duration=300,
                                tabs=[

                                    ft.Tab(
                                        tab_content=Row(
                                            controls=[
                                                Text(value="Métricas Envio", color=colors.ON_BACKGROUND, size=14)
                                            ],
                                        ),
                                        content=Container(
                                            content=DataTable(
                                                sort_column_index=0,
                                                sort_ascending=True,
                                                heading_row_color= ft.colors.SECONDARY_CONTAINER,
                                                heading_row_height=30,
                                                data_row_color={"hovered": ft.colors.PRIMARY_CONTAINER},
                                                divider_thickness=0,
                                                column_spacing=10,
                                                columns=[
                                                    DataColumn(Text("Métricas", color=colors.ON_BACKGROUND, weight="w700", size=14)),
                                                    DataColumn(Text("Loja", color=colors.ON_BACKGROUND, weight="w700", size=14)),
                                                    DataColumn(Text("Meta", color=colors.ON_BACKGROUND, weight="w700", size=14))
                                                ],
                                                rows=[
                                                    DataRow(
                                                        cells=[
                                                            DataCell(Text(value="Taxa de não Cumprimento", color=colors.ON_BACKGROUND)),

                                                            DataCell(Text(value=reputation_shopee["response"]["fulfillment"]["non_fulfillment_rate"]["total_data"]["my_shop_performance"], color=colors.ON_BACKGROUND if float(reputation_shopee["response"]["fulfillment"]["non_fulfillment_rate"]["total_data"]["my_shop_performance"].replace("%", "")) < float(reputation_shopee["response"]["fulfillment"]["non_fulfillment_rate"]["total_data"]["target"].replace("<", "").replace("%", "")) else colors.ERROR)),

                                                            DataCell(Text(value=reputation_shopee["response"]["fulfillment"]["non_fulfillment_rate"]["total_data"]["target"], color=colors.ON_BACKGROUND)),
                                                        ]
                                                    ),
                                                    DataRow(
                                                        cells=[
                                                            DataCell(Text(value="Taxa de Envio Atrasado", color=colors.ON_BACKGROUND)),

                                                            DataCell(Text(value=reputation_shopee["response"]["fulfillment"]["late_shipment_rate"]["total_data"]["my_shop_performance"], color=colors.ON_BACKGROUND if float(reputation_shopee["response"]["fulfillment"]["late_shipment_rate"]["total_data"]["my_shop_performance"].replace("%", "")) < float(reputation_shopee["response"]["fulfillment"]["late_shipment_rate"]["total_data"]["target"].replace("<", "").replace("%", "")) else colors.ERROR)),

                                                            DataCell(Text(value=reputation_shopee["response"]["fulfillment"]["late_shipment_rate"]["total_data"]["target"], color=colors.ON_BACKGROUND)),
                                                        ]
                                                    ),
                                                    DataRow(
                                                        cells=[
                                                            DataCell(Text(value="Tempo de Preparação", color=colors.ON_BACKGROUND)),

                                                            DataCell(Text(value=reputation_shopee["response"]["fulfillment"]["preparation_time"]["total_data"]["my_shop_performance"], color=colors.ON_BACKGROUND if reputation_shopee["response"]["fulfillment"]["preparation_time"]["total_data"]["my_shop_performance"] != None and float(reputation_shopee["response"]["fulfillment"]["preparation_time"]["total_data"]["my_shop_performance"].replace("days", "")) < float(reputation_shopee["response"]["fulfillment"]["preparation_time"]["total_data"]["target"].replace("<", "").replace("days", "")) else colors.ERROR )),

                                                            DataCell(Text(value=reputation_shopee["response"]["fulfillment"]["preparation_time"]["total_data"]["target"], color=colors.ON_BACKGROUND)),
                                                        ]
                                                    ),
                                                ],
                                                width=600,
                                            ),
                                            margin=margin.only(top=10)
                                        )
                                    ),

                                    ft.Tab(
                                        tab_content=Row(
                                            controls=[
                                                Text(value="Métricas Anúncios", color=colors.ON_BACKGROUND, size=14)
                                            ],
                                        ),
                                        content=Container(
                                            content=DataTable(
                                                sort_column_index=0,
                                                sort_ascending=True,
                                                heading_row_color= ft.colors.SECONDARY_CONTAINER,
                                                heading_row_height=30,
                                                data_row_color={"hovered": ft.colors.PRIMARY_CONTAINER},
                                                divider_thickness=0,
                                                column_spacing=10,
                                                columns=[
                                                    DataColumn(Text("Métrica", color=colors.ON_BACKGROUND, weight="w700", size=14)),
                                                    DataColumn(Text("Loja", color=colors.ON_BACKGROUND, weight="w700", size=14)),
                                                    DataColumn(Text("Meta", color=colors.ON_BACKGROUND, weight="w700", size=14))
                                                ],
                                                rows=[
                                                    DataRow(
                                                        cells=[
                                                            DataCell(Text(value="Violações Graves", color=colors.ON_BACKGROUND)),

                                                            DataCell(Text(value=reputation_shopee["response"]["listing_violations"]["severe_listing_violations"]["total_data"]["my_shop_performance"], color=colors.ON_BACKGROUND if float(reputation_shopee["response"]["listing_violations"]["severe_listing_violations"]["total_data"]["my_shop_performance"]) == float(reputation_shopee["response"]["listing_violations"]["severe_listing_violations"]["total_data"]["target"]) else colors.ERROR)),

                                                            DataCell(Text(value=reputation_shopee["response"]["listing_violations"]["severe_listing_violations"]["total_data"]["target"], color=colors.ON_BACKGROUND)),
                                                        ]
                                                    ),
                                                    DataRow(
                                                        cells=[
                                                            DataCell(Text(value="Produtos Pré-encomenda", color=colors.ON_BACKGROUND)),

                                                            DataCell(Text(value=reputation_shopee["response"]["listing_violations"]["pre_order_listing"]["percent_pre_order_listing_data"]["my_shop_performance"], color=colors.ON_BACKGROUND if float(reputation_shopee["response"]["listing_violations"]["pre_order_listing"]["percent_pre_order_listing_data"]["my_shop_performance"].replace("%", "")) <= float(reputation_shopee["response"]["listing_violations"]["pre_order_listing"]["percent_pre_order_listing_data"]["target"].replace("<=", "").replace("%", "")) else colors.ERROR)),

                                                            DataCell(Text(value=reputation_shopee["response"]["listing_violations"]["pre_order_listing"]["percent_pre_order_listing_data"]["target"], color=colors.ON_BACKGROUND)),
                                                        ]
                                                    ),
                                                    DataRow(
                                                        cells=[
                                                            DataCell(Text(value="Outras Violações", color=colors.ON_BACKGROUND)),

                                                            DataCell(Text(value=reputation_shopee["response"]["listing_violations"]["other_listing_violations"]["total_data"]["my_shop_performance"], color=colors.ON_BACKGROUND if float(reputation_shopee["response"]["listing_violations"]["other_listing_violations"]["total_data"]["my_shop_performance"]) == float(reputation_shopee["response"]["listing_violations"]["other_listing_violations"]["total_data"]["target"]) else colors.ERROR)),

                                                            DataCell(Text(value=reputation_shopee["response"]["listing_violations"]["other_listing_violations"]["total_data"]["target"], color=colors.ON_BACKGROUND)),
                                                        ]
                                                    ),
                                                ],
                                                width=600,
                                            ),
                                            margin=margin.only(top=10)
                                        )
                                    ),

                                ],
                                indicator_color=colors.PRIMARY,
                                divider_color=colors.BACKGROUND,
                                tab_alignment= ft.TabAlignment.CENTER,
                                height=230,
                                width=600,
                            ),

                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER
                    )
                
                except Exception as exc:
                    print(f'\n❌ REPUTATION > get_reputation() ==> EXCEPTION IN SHOPEE ({company}): {exc}\n')
                    return None
                    # return Column(
                    #     controls=[
                    #         Container(
                    #             content=Text(value="❌ ERRO AO CONSULTAR"),
                    #             padding=padding.symmetric(10),
                    #             alignment=alignment.center
                    #         )
                    #     ],
                    #     horizontal_alignment=CrossAxisAlignment.CENTER
                    # ) 

            case _:
                return Column(
                    controls=[
                        Container(
                            content=Text(value="❌ REPUTAÇÃO NÃO DISPONÍVEL"),
                            padding=padding.symmetric(10),
                            alignment=alignment.center
                        )
                    ],
                    horizontal_alignment=CrossAxisAlignment.CENTER
                )

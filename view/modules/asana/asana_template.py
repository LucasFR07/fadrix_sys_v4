import flet as ft
from view.modules.asana.asana_get import AsanaGet
from view.component.snackbar import SnackBar_PATTERNS


class AsanaTemplate(AsanaGet):

    def __init__(self, page:ft.Page, task:dict, event_create, event_delete) -> None:
        super().__init__(task)
        self.page = page
        self.create_task_event = event_create
        self.delete_task_event = event_delete

        ## WIDGETS:
        self.snackbar = SnackBar_PATTERNS(self.page)
        ## ---------


    def create_template(self):
        """ Cria o template para visualização pelo usuário. """

        set_content_task = list()
        set_task = self.get_task()
        # print(f'\n🐞 ##DEBUG >> ASANA_TEMPLATE > create_template() == SET_TASK: {set_task}\n') ##DEBUG

        if len(set_task) > 0:
            for task_key, task in set_task.items():
                # print(f'\n🐞 ##DEBUG >> ASANA_TEMPLATE > create_template() == TASK: {task}\n') ##DEBUG

                status_completed = {
                    True: {"icon":ft.icons.CHECK_CIRCLE_ROUNDED, "color":ft.colors.GREEN},
                    False: {"icon":ft.icons.CHECK_CIRCLE_OUTLINE, "color":ft.colors.ON_BACKGROUND},
                    None: {"icon":ft.icons.DELETE_FOREVER_OUTLINED, "color":ft.colors.RED}
                }

                if task["delet"] == True:
                    set_content_task.append(
                        ft.Container(
                            content=ft.Column(
                                controls=[

                                    ft.Container(
                                        content=ft.ListTile(
                                            leading=ft.Icon(
                                                name=status_completed[task["completed"]]["icon"],
                                                color=status_completed[task["completed"]]["color"],
                                                size=20
                                            ),
                                            title=ft.Text(value=task["name"], size=14, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_600),
                                            content_padding=ft.padding.symmetric(5,7),
                                            dense=True,
                                        ),
                                        bgcolor=ft.colors.with_opacity(0.8, ft.colors.BACKGROUND),
                                        padding=ft.padding.symmetric(10,5),
                                        margin=ft.margin.only(bottom=5),
                                        alignment=ft.alignment.center
                                    ),
                                    ft.Container(height=5),
                                    ft.Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.15),
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                    ft.Row(controls=[ft.Icon(name=ft.icons.PERM_IDENTITY, size=13, color=ft.colors.ON_BACKGROUND), ft.Text(value="ID: ", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND), ft.Text(value=task["gid"], size=11, color=ft.colors.ON_BACKGROUND, selectable=True)], spacing=1),

                                                    ft.Text(value="|", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND),

                                                    ft.Row(controls=[ft.Icon(name=ft.icons.LINK_OUTLINED, size=13, color=ft.colors.ON_BACKGROUND), ft.Text(value="LINK: ", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND), ft.Text(spans=[ft.TextSpan(text="ABRIR ASANA", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=11, color=ft.colors.ON_BACKGROUND), url=task['link'])])], spacing=1),

                                                    ft.Text(value="|", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND),

                                                    ft.Row(controls=[ft.Icon(name=ft.icons.DELETE_ROUNDED, size=13, color=ft.colors.ON_BACKGROUND), ft.Container(content=ft.Text(value="Deletar", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND), tooltip="Deletar a tarefa no Asana", on_click=self.delete_task_event)], spacing=1),
                                            ],
                                            spacing=15,
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                    )                                    

                                ],
                                spacing=10
                            ),
                            border=ft.border.all(0.5, ft.colors.with_opacity(1, ft.colors.SURFACE_VARIANT)),
                            bgcolor=ft.colors.with_opacity(0.3, ft.colors.SURFACE_VARIANT),
                            border_radius=ft.border_radius.all(10),
                            padding=ft.padding.symmetric(10,7),
                            col=6
                        )
                    )
                    return ft.ResponsiveRow(controls=set_content_task)

                set_content_task.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[

                                ft.Container(
                                    content=ft.ListTile(
                                        leading=ft.Icon(
                                            name=status_completed[task["completed"]]["icon"],
                                            color=status_completed[task["completed"]]["color"],
                                            size=20
                                        ),
                                        title=ft.Text(value=task["name"], size=14, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_600),
                                        content_padding=ft.padding.symmetric(5,7),
                                        dense=True,
                                    ),
                                    bgcolor=ft.colors.with_opacity(0.8, ft.colors.BACKGROUND),
                                    padding=ft.padding.symmetric(10,5),
                                    margin=ft.margin.only(bottom=5),
                                    alignment=ft.alignment.center
                                ),

                                ft.Row(
                                    controls=[
                                        ft.Text(value='Responsável', size=10, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_300, width=100),
                                        ft.Row(
                                            controls=[
                                                ft.Image(src=task['assignee']['assignee_photo'], width=21, border_radius=100),
                                                ft.Text(value=task['assignee']['assignee_name'], size=11, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_600),
                                            ],
                                            spacing=5,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                                        ),
                                    ]
                                ),

                                ft.Row(
                                    controls=[
                                        ft.Text(value='Data de Conclusão', size=10, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_300, width=100),
                                        ft.Text(value=task['data_completed'], size=11, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_600),
                                    ]
                                ),

                                ft.Row(
                                    controls=[
                                        ft.Text(value='Projetos', size=10, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_300, width=100),
                                        ft.Column(
                                            controls=[
                                                ft.Container(
                                                    content=ft.Column(
                                                        controls=[
                                                            ft.Text(value=pjt['project_name'], size=11, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_700),
                                                            ft.Text(value=f'> {pjt['section_name']}', size=11, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_300)
                                                        ],
                                                        spacing=2,
                                                        alignment=ft.MainAxisAlignment.START
                                                    ),
                                                    border=ft.border.all(0.5, ft.colors.with_opacity(0.7, ft.colors.OUTLINE)),
                                                    border_radius=ft.border_radius.all(5),
                                                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.OUTLINE),
                                                    padding=ft.padding.symmetric(4,7),
                                                    alignment=ft.alignment.center
                                                ) for pjt in task['projects']
                                            ]
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.START
                                ),

                                ft.Row(
                                    controls=[
                                        ft.Text(value='Status', size=10, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_300, width=100),
                                        ft.Container(
                                            content=ft.Text(value=task['status']["name"], size=11, color=ft.colors.ON_BACKGROUND, weight=ft.FontWeight.W_600),
                                            border=ft.border.all(0.5, ft.colors.with_opacity(0.7, f'{task['status']["color"]}')),
                                            border_radius=ft.border_radius.all(5),
                                            bgcolor=ft.colors.with_opacity(0.7, f'{task['status']["color"]}'),
                                            padding=ft.padding.symmetric(4,7),
                                            alignment=ft.alignment.center
                                        ),
                                    ]
                                ),

                                ft.Container(height=5),
                                ft.Divider(height=1, color=ft.colors.ON_BACKGROUND, opacity=0.15),

                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                                ft.Row(controls=[ft.Icon(name=ft.icons.PERM_IDENTITY, size=13, color=ft.colors.ON_BACKGROUND), ft.Text(value="ID: ", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND), ft.Text(value=task["gid"], size=11, color=ft.colors.ON_BACKGROUND, selectable=True)], spacing=1),
                                                
                                                ft.Text(value="|", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND),

                                                ft.Row(controls=[ft.Icon(name=ft.icons.LINK_OUTLINED, size=13, color=ft.colors.ON_BACKGROUND), ft.Text(value="LINK: ", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND), ft.Text(spans=[ft.TextSpan(text="ABRIR ASANA", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=11, color=ft.colors.ON_BACKGROUND), url=task['link'])])], spacing=1),

                                                ft.Text(value="|", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND),

                                                ft.Row(controls=[ft.Icon(name=ft.icons.DELETE_ROUNDED, size=13, color=ft.colors.ON_BACKGROUND), ft.Container(content=ft.Text(value="Deletar", weight=ft.FontWeight.W_700, size=11, color=ft.colors.ON_BACKGROUND), tooltip="Deletar a tarefa no Asana", on_click=self.delete_task_event)], spacing=1),
                                        ],
                                        spacing=15,
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                )

                            ],
                            spacing=10
                        ),
                        border=ft.border.all(0.5, ft.colors.with_opacity(1, ft.colors.SURFACE_VARIANT)),
                        bgcolor=ft.colors.with_opacity(0.3, ft.colors.SURFACE_VARIANT),
                        border_radius=ft.border_radius.all(10),
                        padding=ft.padding.symmetric(10,7),
                        col=6
                    )
                )

            return ft.ResponsiveRow(controls=set_content_task)


        else:
            self.snackbar.not_found("Tarefa Asana não encontrada.")
            self.page.update()
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(value="Nenhuma tarefa Asana encontrada para esse pedido.\nClique no botão abaixo para criar uma nova tarefa."),
                        ft.FilledButton(text="Criar Tarefa Asana", on_click=self.create_task_event)
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=ft.padding.symmetric(15,20),
                margin=ft.margin.symmetric(10,10),
                alignment=ft.alignment.center_left
            )

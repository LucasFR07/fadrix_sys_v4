import flet as ft
from flet import ( Page, AppBar, IconButton, PopupMenuItem, PopupMenuButton, Text, Container, Row, Image, icons, margin)

## CONEXÃO COM DADOS
from data.repository.userV2 import UserV2Repository as USER
from data.repository.notice import NoticeRepository as NOTICE
from sqlalchemy import null

## COMPONENTES TEMPLATE
from view.component.buttons import ButtonsComponents as BTN
from view.component.dialog import Dialog
from view.component.snackbar import SnackBar_PATTERNS

## CONTROLES DO SISTEMA
from datetime import time, datetime
from controllers.date_control import date_create as DATE
from controllers.notice_control import NoticeControl


class AppBar(AppBar):

    def __init__(self, page:Page, user, drawer):
        super().__init__()
        self.page = page
        self.user_system = user
        self.new_popmenuitem = None

        ## WIDGETS:
        self.alert = Dialog(self.page)
        self.snackbar = SnackBar_PATTERNS(self.page)
        ## ---------

        def on_notification_broadcast(notice:PopupMenuItem):

            """ Transmite a notificação para todas as sessões ativas do sistema. """

            try:
                self.icon_notice.name=icons.NOTIFICATIONS_ACTIVE_ROUNDED
                self.icon_notice.color=ft.colors.TERTIARY_CONTAINER
                self.icon_notice.update()

                self.new_popmenuitem = PopupMenuItem()

                if len(self.notice_box.items) == 0:
                    self.notice_box.items.clear()

                self.notice_box.items.insert(0, notice)
                self.notice_box.items.insert(1, self.new_popmenuitem)

                self.snackbar.notify()
                self.new_popmenuitem = None
                self.page.update()

            except Exception as exc:
                print(f'\n❌ APPBAR > on_notification_broadcast() ==> EXCEPTION: {exc}\n')
                self.new_popmenuitem = None
                self.snackbar.notify()
                # self.page.update()


        self.page.pubsub.subscribe(on_notification_broadcast)

        self.icon_light = ft.Ref[IconButton]()


        self.leading = IconButton(icons.MENU_ROUNDED, icon_color=ft.colors.BACKGROUND, on_click=drawer)
        self.leading_width = 50
        self.title = Image(src="assets/images/system/LOGOMARCA_FADRIX__WHITE.png", width=80)
        self.center_title = False
        self.toolbar_height = 50
        self.color = ft.colors.BACKGROUND
        self.bgcolor = ft.colors.PRIMARY

        self.icon_notice = ft.Icon(name=icons.NOTIFICATIONS_NONE, color=ft.colors.BACKGROUND)

        self.notice_box = PopupMenuButton(
            content=self.icon_notice,
            items=[PopupMenuItem(text="Nenhuma notificação")],
            height=450,
            tooltip="Notificações do Sistema",
            on_cancelled=self.__clear_notice
        )

        self.get_notices = NOTICE().filter_all()
        if len(self.get_notices) > 0:
            self.get_notices.reverse()
            self.notice_box.items.clear()
            for notice in self.get_notices[0:20]:
                self.notice_box.items.append(
                    NoticeControl(
                        page=self.page,
                        topic=notice.topic,
                        title=notice.title,
                        messagem=notice.messagem,
                        action=notice.action,
                        link=notice.link,
                        user=notice.user,
                        date=notice.date
                    ).return_notice()
                )
                # self.notice_box.items.append(ft.Container(content=ft.Divider(height=0.3), margin=margin.symmetric(vertical=15), disabled=True))
                self.notice_box.items.append(PopupMenuItem())

            self.notice_box.items.pop()


        self.actions = [
            Container(
                content=Row(
                    controls=[
                        self.notice_box,
                        IconButton(icon=icons.NOTIFICATION_ADD_ROUNDED, icon_color=ft.colors.BACKGROUND, on_click=self.__open_box_notice, visible=False if self.user_system['user'] != 'admin@fadrixsys' else True),
                        IconButton(icon=icons.LIGHT_MODE_OUTLINED if self.user_system["theme_light"] == "dark" else icons.DARK_MODE_OUTLINED, icon_color=ft.colors.BACKGROUND, ref=self.icon_light, on_click=self.light_mode),
                        PopupMenuButton(
                            content=ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.BACKGROUND),
                            items=[
                                PopupMenuItem(text="Cores do Tema:"),
                                PopupMenuItem(),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.RED), Text("Red", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="red"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.PINK), Text("Pink", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="pink"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.PURPLE), Text("Purple", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="purple"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.DEEP_PURPLE), Text("Deep Purple", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="deeppurple"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.INDIGO), Text("Indigo", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="indigo"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.BLUE), Text("Blue", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="blue"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.LIGHT_BLUE), Text("Light Blue", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="lightblue"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.CYAN), Text("Cyan", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="cyan"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.TEAL), Text("Teal", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="teal"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.GREEN), Text("Green", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="green"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.LIGHT_GREEN), Text("Light Green", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="lightgreen"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.LIME), Text("Lime", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="lime"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.YELLOW), Text("Yellow", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="yellow"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.AMBER), Text("Amber", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="amber"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.ORANGE), Text("Orange", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="orange"),
                                PopupMenuItem(content=Row(controls=[ft.Icon(icons.PALETTE_OUTLINED, color=ft.colors.BROWN), Text("Brown", color=ft.colors.ON_BACKGROUND)]), on_click=self.color_mode, data="brown"),
                            ]
                        ),         
                    ],
                    spacing=20
                ),
                margin=margin.only(right=15)
            )
        ]


    def light_mode(self, e):

        """ Define o modo escuro, personalizado para o usuário. """

        match self.user_system["theme_light"]:

            case "light":
                e.control.icon = icons.LIGHT_MODE_OUTLINED
                USER().update(id=self.user_system["id"], fild="theme_light", data="dark")
                self.user_system["theme_light"] = "dark"
                self.page.client_storage.set(key="user_info", value=self.user_system)
                self.page.theme_mode = "dark"
                self.page.update()

            case "dark":
                e.control.icon = icons.DARK_MODE_OUTLINED
                USER().update(id=self.user_system["id"], fild="theme_light", data="light")
                self.user_system["theme_light"] = "light"
                self.page.client_storage.set(key="user_info", value=self.user_system)
                self.page.theme_mode = "light"
                self.page.update()


    def color_mode(self, e):

        """ Define a cor padrão de tema do sistema, personalizado para o usuário. """

        color = e.control.data
        self.page.theme = ft.Theme(color_scheme_seed=color)
        USER().update(id=self.user_system["id"], fild="theme_color", data=color)
        self.user_system['theme_color'] = color
        self.page.client_storage.set(key="user_info", value=self.user_system)
        self.page.update()


    def __open_box_notice(self, e):

        try:

            self.notice_topic = ft.Dropdown(
                value=None,
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                filled=True,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                content_padding=ft.padding.symmetric(vertical=7, horizontal=10),
                height=40,
                alignment=ft.alignment.center_left,
                options=[
                    ft.dropdown.Option("Atualização"),
                    ft.dropdown.Option("Relatório"),
                    ft.dropdown.Option("Recado"),
                ]
            )

            self.notice_title = ft.TextField(
                value=None,
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                content_padding=ft.padding.symmetric(7,10),
                height=40
            )

            self.notice_msg = ft.TextField(
                value=None,
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                multiline=True,
                min_lines=4,
                max_lines=4
            )

            self.notice_action = ft.Dropdown(
                value=None,
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                filled=True,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                content_padding=ft.padding.symmetric(vertical=7, horizontal=10),
                height=40,
                alignment=ft.alignment.center_left,
                options=[
                    ft.dropdown.Option("Download"),
                    ft.dropdown.Option("Diálogo")
                ]
            )

            self.notice_link = ft.TextField(
                value=None,
                text_style=ft.TextStyle(size=16, weight="w600"),
                color=ft.colors.ON_BACKGROUND,
                bgcolor=ft.colors.BACKGROUND,
                border_color=ft.colors.OUTLINE,
                border_radius=5,
                focused_color=ft.colors.PRIMARY,
                focused_border_color=ft.colors.PRIMARY,
                content_padding=ft.padding.symmetric(7,10),
                height=40
            )

            content = ft.Column(
                controls=[
                    ft.Column(
                        controls=[
                            Row(
                                controls=[
                                    ft.Icon(name=icons.TOPIC, size=13, color=ft.colors.ON_BACKGROUND),
                                    Text(value="Tópico", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                ],
                                spacing=3
                            ),
                            self.notice_topic
                        ],
                        spacing=5
                    ),

                    ft.Column(
                        controls=[
                            Row(
                                controls=[
                                    ft.Icon(name=icons.TEXT_FIELDS, size=13, color=ft.colors.ON_BACKGROUND),
                                    Text(value="Título da Notificação", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                ],
                                spacing=3
                            ),
                            self.notice_title
                        ],
                        spacing=5
                    ),

                    ft.Column(
                        controls=[
                            Row(
                                controls=[
                                    ft.Icon(name=icons.TEXT_FIELDS, size=13, color=ft.colors.ON_BACKGROUND),
                                    Text(value="Mensagem da Notificação", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                ],
                                spacing=3
                            ),
                            self.notice_msg
                        ],
                        spacing=5
                    ),

                    ft.ResponsiveRow(
                        controls=[

                            ft.Column(
                                controls=[
                                    Row(
                                        controls=[
                                            ft.Icon(name=icons.DATASET_LINKED_SHARP, size=13, color=ft.colors.ON_BACKGROUND),
                                            Text(value="Tipo de Ação", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                        ],
                                        spacing=3
                                    ),
                                    self.notice_action
                                ],
                                spacing=5,
                                col=4
                            ),

                            ft.Column(
                                controls=[
                                    Row(
                                        controls=[
                                            ft.Icon(name=icons.INSERT_LINK, size=13, color=ft.colors.ON_BACKGROUND),
                                            Text(value="Link Redirecionamento", size=13, weight="w500", color=ft.colors.ON_BACKGROUND)
                                        ],
                                        spacing=3
                                    ),
                                    self.notice_link
                                ],
                                spacing=5,
                                col=8
                            ),

                        ]
                    )
                ],
                spacing=20,
                width=550,
                height=400
            )

            self.alert.default_dialog(
                title=Container(
                    content=Row(
                        controls=[
                            Row(
                                controls=[
                                    ft.Icon(name=icons.EDIT_NOTIFICATIONS_SHARP, color=ft.colors.ON_BACKGROUND),
                                    Text("Criar Notificação".upper(), size=18, weight=ft.FontWeight.W_600, color=ft.colors.ON_BACKGROUND)
                                ]
                            ),
                            BTN(self.page, text="notificar", style="default", event=self.__new_notice)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=ft.border_radius.all(5),
                    padding=ft.padding.symmetric(15,10)
                ),
                contt=content,
                act=[]
            )

            self.page.dialog=self.alert
            self.alert.open=True
            self.page.update()

        except Exception as exc:
            print(f'\n❌ APPBAR > __open_box_notice() == EXCEPTION: {exc} \n')


    def __new_notice(self, e):

        """ Envia a notificação para os usuários. """

        try:
            if self.notice_topic.value == None or self.notice_action.value == None:
                self.snackbar.warning("Selecione um tópico/ação de notificação para continuar.")
                self.page.update()
                return None

            if len(self.notice_link.value) == 0 and self.notice_action.value != "Diálogo":
                self.snackbar.warning("Informe um link válido para a ação selecionada.")
                self.page.update()
                return None

            verifica_textfild = [self.notice_title.value, self.notice_msg.value]

            for textfild in verifica_textfild:
                if textfild == None or len(textfild) <= 3:
                    self.snackbar.warning("Informe um título/descrição válido para continuar.")
                    self.page.update()
                    return None

            new_notice = NoticeControl(
                page=self.page,
                topic=self.notice_topic.value,
                title=self.notice_title.value,
                messagem=self.notice_msg.value,
                action=self.notice_action.value,
                link=self.notice_link.value if self.notice_action.value != "Diálogo" else None,
                user=self.user_system['name']
            )

            save_notice = new_notice.create_notice()

            if save_notice:
                self.page.pubsub.send_all(new_notice.return_notice())
            else:
                self.snackbar.internal_error()

            self.alert.open=False
            self.page.update()

        except Exception as exc:
            print(f'\n❌ APPBAR > __new_notice() == EXCEPTION: {exc} \n')
            self.snackbar.internal_error()
            self.alert.open=False
            self.page.update()
            return None


    def __clear_notice(self, e):

        self.icon_notice.name=icons.NOTIFICATIONS_NONE
        self.icon_notice.color=ft.colors.BACKGROUND
        self.icon_notice.update()
        self.page.update()

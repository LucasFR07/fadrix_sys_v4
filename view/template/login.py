from pathlib import Path
import json
import flet as ft
from flet import ( Page, UserControl, Text, TextField, Container, Row, ResponsiveRow, Column, Ref, Image, ImageFit, InputBorder, MainAxisAlignment, CrossAxisAlignment, MaterialState, RoundedRectangleBorder, FilledButton, ElevatedButton, BoxShadow, ButtonStyle, ShadowBlurStyle, Icon, icons, margin, padding, colors, alignment, Offset )

## CONTROLES DO SISTEMA
from controllers.user_control import UserControl as UC
from controllers.date_control import date_create as DATE

config = Path('C:/Users/marketing/Downloads/V4/V4/config/app.json')
if config.exists():
    with open(config, "r", encoding='utf-8') as f:
        APP_CONFIG = json.load(f)
else:
    APP_CONFIG = {"app": {"name": "Fadrix SYS", "version": "4.0", "build": "b2024.11.01"}}



class UserLogin(UserControl):

    """ View de exibição da tela de login do sistema """

    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.user = None
        self.passwd = None 

        self.info_system = APP_CONFIG


    def build(self):

        ## VARIÁVEIS (REFs):
        self.login_button = Ref[FilledButton]()
        self.erro_login = Ref[Container]()
        self.erro_message = Ref[Text]()
        ## ---------

        view = Container(
            content=ResponsiveRow(
                controls=[
                    Container(
                        content=Column(
                            controls=[
                                Column(
                                    controls=[
                                        Text(value=self.info_system["app"]["name"], size=22, weight=ft.FontWeight.W_800, color=colors.PRIMARY, text_align=ft.TextAlign.CENTER),
                                        Text(value=self.info_system["app"]["description"], size=15, weight=ft.FontWeight.W_400, color=colors.ON_BACKGROUND, text_align=ft.TextAlign.CENTER, width=350),
                                    ],
                                    height=150,
                                    alignment=MainAxisAlignment.CENTER,
                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                    spacing=5
                                ),
                                Image(src="V4/assets/images/system/avatar_login.png", height=250),
                                Text(value=f'{self.info_system["app"]["name"]} v{self.info_system["app"]["version"]} - {self.info_system["app"]["build"]}', size=12, weight=ft.FontWeight.W_600, color=colors.ON_BACKGROUND, text_align=ft.TextAlign.CENTER)
                            ],
                            alignment=MainAxisAlignment.SPACE_AROUND,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            spacing=5
                        ),
                        alignment=alignment.center,
                        col=6
                    ),
                    Container(
                        content=Column(
                            controls=[
                                Container(
                                    content=Column(
                                        controls=[
                                            Container(
                                                content=Column(
                                                    controls=[
                                                        Image(src="V4/assets/images/system/LOGOMARCA_FADRIX21__BLACK_COLOR.png" if self.page.theme_mode == "light" else "V4/assets/images/system/LOGOMARCA_FADRIX21__WHITE_COLOR.png", height=65),
                                                        Text(value="acesse sua conta agora", weight="w400", color=ft.colors.ON_BACKGROUND, size=13, text_align="center"),
                                                    ],
                                                    horizontal_alignment=CrossAxisAlignment.CENTER,
                                                    alignment=MainAxisAlignment.CENTER,
                                                    spacing=5
                                                ),
                                                margin=margin.symmetric(15,20),
                                                alignment=alignment.center
                                            ),
                                            Column(
                                                [
                                                    Text(value="Usuário:", weight="w500", color=ft.colors.ON_BACKGROUND),
                                                    TextField(
                                                        value="",
                                                        suffix_text="@fadrixsys",
                                                        text_style=ft.TextStyle(size=14, weight="w600"),
                                                        color=ft.colors.ON_BACKGROUND,
                                                        bgcolor=colors.SURFACE_VARIANT,
                                                        border_color=colors.with_opacity(0.3, colors.OUTLINE),
                                                        border_radius=5,
                                                        focused_color=ft.colors.PRIMARY,
                                                        focused_border_color=ft.colors.PRIMARY,
                                                        content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                        height=40,
                                                        on_blur=self.verify_fild,
                                                        on_change=self.get_user
                                                    ),
                                                ],
                                                spacing=0
                                            ),
                                            Column(
                                                [
                                                    Text(value="Senha:", weight="w500", color=ft.colors.ON_BACKGROUND),
                                                    TextField(
                                                        value="",
                                                        password=True,
                                                        can_reveal_password=True,
                                                        text_style=ft.TextStyle(size=14, weight="w600"),
                                                        color=ft.colors.ON_BACKGROUND,
                                                        bgcolor=colors.SURFACE_VARIANT,
                                                        border_color=colors.with_opacity(0.3, colors.OUTLINE),
                                                        border_radius=5,
                                                        focused_color=ft.colors.PRIMARY,
                                                        focused_border_color=ft.colors.PRIMARY,
                                                        content_padding=padding.symmetric(vertical=1, horizontal=10),
                                                        height=40,
                                                        on_blur=self.verify_fild,
                                                        on_change=self.get_passwd
                                                    ),
                                                ],
                                                spacing=0
                                            ),
                                            Container(
                                                content=Row(
                                                    controls=[
                                                        Icon(icons.WARNING_AMBER_ROUNDED, color=ft.colors.ERROR, size=20),
                                                        Text(color=ft.colors.ERROR, ref=self.erro_message, text_align=ft.TextAlign.CENTER)
                                                    ], 
                                                    alignment=MainAxisAlignment.CENTER,
                                                    vertical_alignment=CrossAxisAlignment.CENTER,
                                                    wrap=True
                                                ),
                                                padding=padding.symmetric(10, 5),
                                                visible=False,
                                                ref=self.erro_login
                                            ),
                                            Container(height=5),
                                            Row(
                                                controls=[
                                                    ElevatedButton(
                                                        icon=icons.LOGIN_OUTLINED,
                                                        text="Entrar",
                                                        style=ButtonStyle(
                                                            color={
                                                                MaterialState.HOVERED: ft.colors.BACKGROUND,
                                                                MaterialState.DEFAULT: ft.colors.BACKGROUND,
                                                            },
                                                            bgcolor={
                                                                MaterialState.HOVERED: ft.colors.INVERSE_PRIMARY,
                                                                MaterialState.DEFAULT: ft.colors.PRIMARY
                                                            },
                                                            overlay_color=colors.TRANSPARENT,
                                                            elevation={"pressed": 0, "": 1},
                                                            animation_duration=500,
                                                            shape={
                                                                MaterialState.HOVERED: RoundedRectangleBorder(radius=10),
                                                                MaterialState.DEFAULT: RoundedRectangleBorder(radius=10),
                                                            },                                                
                                                        ),
                                                        ref=self.login_button,
                                                        on_click=self.verify_login,
                                                        expand=True                                            
                                                    ),
                                                ],
                                                alignment=MainAxisAlignment.CENTER
                                            )
                                        ],
                                        width=250,
                                        spacing=10,
                                        horizontal_alignment=CrossAxisAlignment.START,
                                        col=3
                                    ),
                                    bgcolor=ft.colors.BACKGROUND,
                                    margin=margin.symmetric(10,20),
                                    padding=padding.all(30),
                                    border_radius=7,
                                    shadow=BoxShadow(
                                        spread_radius=0.5,
                                        blur_radius=2,
                                        color=ft.colors.OUTLINE,
                                        offset=Offset(0, 0),
                                        blur_style=ShadowBlurStyle.OUTER,
                                    ),
                                ),

                            ],
                            alignment=MainAxisAlignment.CENTER,
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            spacing=5
                        ),
                        bgcolor=colors.PRIMARY,
                        alignment=alignment.top_center,
                        col=6
                    )
                ]
            ),
            width=900,
            height=550,
            bgcolor=colors.BACKGROUND,
            border_radius=20,
            shadow=BoxShadow(
                spread_radius=0.5,
                blur_radius=5,
                color=ft.colors.OUTLINE,
                offset=Offset(0, 3),
                blur_style=ShadowBlurStyle.NORMAL,
            ),
            col={"sm": 4, "md": 3, "xl": 3},
        )

        return Container(content=view, alignment=alignment.center)


    def verify_fild(self, e):

        """ Função para validar se os campos obrigatórios estão preenchidos """

        # if e.control.value == "":
        #     e.control.error_text = "*obrigatório"
        #     self.login_button.current.disabled = True
        #     self.update()

        pass


    def get_user(self, e):

        """ Função para obter a entrada de usuário """

        e.control.error_text = None
        self.login_button.current.disabled = False
        self.user = e.control.value
        self.update()


    def get_passwd(self, e):

        """ Função para obter a entrada de senha """

        e.control.error_text = None
        self.login_button.current.disabled = False
        self.passwd = e.control.value
        self.update()        


    def verify_login(self, e):

        """ Função para validar usuário e senha """

        try:

            if self.user == None or self.passwd == None:
                self.erro_message.current.value = "usuário e senha são obrigatórios"
                self.erro_login.current.visible = True
                self.erro_login.current.update()
                self.page.update()
                return None

            self.login_account = UC().login(user=f'{self.user}@fadrixsys', password=self.passwd, session=self.page.session_id)

            match self.login_account["status"]:

                case "error":
                    self.erro_message.current.value = self.login_account["message"]
                    self.erro_login.current.visible = True
                    self.erro_login.current.update()
                    self.page.update()
                    return None
                
                case "ok":
                    print(f'\n{"-"*60}\n [OK] NOVO LOGIN DE USUARIO\n\n [USER] USUARIO = {self.login_account["user"]["user"]} | {DATE().strftime("%d/%m/%Y %H:%M:%S")}\n [NET] CLIENT IP = {self.page.client_ip}\n [NET] PLATFORM = {(self.page.platform).upper()}\n [NET] CLIENT AGENTE = {self.page.client_user_agent}\n [NET] SESSION ID = {self.page.session_id}\n{"-"*60}\n') ##DEBUG

                    self.page.client_storage.set(key="user_info", value=self.login_account["user"])
                    self.page.go("/pedidos")


        except Exception as exc:
            print(f'\n[ERRO] LOGIN > verify_login() ==> EXCEPTION: {exc}\n')
            self.erro_message.current.value = "Erro de login, favor verifique o usuário e senha informados."
            self.erro_login.current.visible = True
            self.erro_login.current.update()
            self.page.update()
            return None

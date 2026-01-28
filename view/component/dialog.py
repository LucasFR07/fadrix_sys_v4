import flet as ft
from flet import ( 
    Page, AlertDialog, Container, Column, Row,
    Text, TextAlign, Icon, ProgressRing,
    MainAxisAlignment, CrossAxisAlignment, RoundedRectangleBorder,
    icons, padding, margin
)


class Dialog(AlertDialog):

    def __init__(self, page:Page):
        super().__init__()
        self.page = page

        self.modal = False
        self.title_padding = padding.all(0)
        self.content_padding = padding.all(40)
        self.actions_padding = padding.all(0)        
        self.shape = RoundedRectangleBorder(radius=25)
        self.on_dismiss = self.__dismiss


    def __dismiss(self, e):
        self.open = False
        self.update
        self.content, self.actions, self.title = None, None, None


    def close_dialog(self):
        self.open = False
        self.update
        self.content, self.actions, self.title = None, None, None


    def default_dialog(self, contt, act:list, title=None):

        """ Diálogo padrão - apresenta informações diversas do sistema. """

        if title != None:
            self.title = title
            self.title_padding = padding.only(top=25, left=25, right=25)

        self.content = contt
        self.content_padding = padding.all(25)
        self.actions = act
        self.actions_padding = padding.only(bottom=25)
        self.actions_alignment = MainAxisAlignment.CENTER
        return self


    def progress_dialog(self, text:str):

        """ Dialogo progresso - informar ao usuário que uma tarefa está sendo executada de fundo. Ex.: salvando um pedido no sistema. """

        self.content = Column(
            controls=[
                Container(
                    content=ProgressRing(
                        color=ft.colors.PRIMARY
                    ),
                    margin=margin.symmetric(vertical=10)
                ),
                Text(value=text, size=16, weight="w300", text_align=TextAlign.CENTER, color=ft.colors.ON_BACKGROUND)
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            height=100
        )

        self.modal = True
        return self


    def info_dialog(self, text:str, act:list):

        """ Diálogo de informação - apresenta informações para o usuário tomar uma decisão. """

        self.content = Column(
            controls=[
                Container(
                    content=Icon(icons.INFO_OUTLINE_ROUNDED, size=38, color=ft.colors.PRIMARY),
                ),
                Container(
                    content=Text(value=text, size=18, weight="w400", text_align=TextAlign.CENTER, color=ft.colors.ON_BACKGROUND),
                    margin=margin.symmetric(vertical=10)
                ),
                Container(
                    content=Row(
                        controls=act,
                        alignment=MainAxisAlignment.CENTER
                    ),
                    margin=margin.symmetric(vertical=10)
                )
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            width=400,
            height=180
        )

        return self


    def warning_dialog(self, text:str):

        """ Diálogo de alerta - apresenta avisos de alerta para o usuário. """

        self.content = Column(
            controls=[
                Container(
                    content=Icon(icons.WARNING_ROUNDED, size=40, color=ft.colors.ERROR),
                ),
                Container(
                    content=Text(value=text, size=20, weight="w400", text_align=TextAlign, color=ft.colors.ON_BACKGROUND),
                    margin=margin.symmetric(vertical=10)
                )
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            width=400,
            height=180
        )

        return self

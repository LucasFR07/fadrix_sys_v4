import flet as ft
from flet import (Page, SnackBar, Row, Text, Icon, icons )


class SnackBar_PATTERNS:

    """ Classe com SnackBar predefinidos para avisos padrões do sistema. """

    def __init__(self, page:Page) -> None:
        self.page = page


    def sucess(self, msg:str) -> SnackBar:

        """ Snackbar para confirmar uma ação bem sucedia. """

        ICON_SNACK = Icon(name=icons.CHECK_CIRCLE_OUTLINED, color=ft.colors.BACKGROUND, size=18)
        MSG_SNACK = Text(value=msg, color=ft.colors.BACKGROUND, size=16, weight="w600")

        self.page.snack_bar = SnackBar(
            content = Row(controls=[ICON_SNACK, MSG_SNACK]),
            bgcolor = ft.colors.LIGHT_GREEN_700,
            behavior= ft.SnackBarBehavior.FLOATING,
            width = int((len(msg)*10)+25),
            open = True
        )

        self.page.update()


    def notify(self) -> SnackBar:

        """ Snackbar para alertar sobre uma nova notificação do sistema. """

        ICON_SNACK = Icon(name=icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=ft.colors.BACKGROUND, size=18)
        MSG_SNACK = Text(value="Nova Notificação!", color=ft.colors.BACKGROUND, size=16, weight="w600")

        self.page.snack_bar = SnackBar(
            content = Row(controls=[ICON_SNACK, MSG_SNACK]),
            bgcolor = ft.colors.LIGHT_GREEN_700,
            behavior= ft.SnackBarBehavior.FLOATING,
            width = 200,
            open = True
        )

        self.page.update()


    def clipboard(self) -> SnackBar:

        """ Snackbar para cliboard. """

        ICON_SNACK = Icon(name=icons.CONTENT_COPY, color=ft.colors.BACKGROUND, size=18)
        MSG_SNACK = Text(value="Copiado para área de transferência.", color=ft.colors.BACKGROUND, size=16, weight="w600")

        self.page.snack_bar = SnackBar(
            content = Row(controls=[ICON_SNACK, MSG_SNACK]),
            bgcolor = ft.colors.LIGHT_GREEN_700,
            behavior= ft.SnackBarBehavior.FLOATING,
            width = 330,
            open = True
        )

        self.page.update()


    def download(self, event, msg:str="Download Disponível") -> SnackBar:

        """ Snackbar para confirmar download de relatórios e arquivos. """

        ICON_SNACK = Icon(name=icons.DOWNLOADING_SHARP, color=ft.colors.BACKGROUND, size=18)
        MSG_SNACK = Text(value=msg, color=ft.colors.BACKGROUND, size=16, weight="w600")

        self.page.snack_bar = SnackBar(
            content = Row(controls=[ICON_SNACK, MSG_SNACK]),
            bgcolor = ft.colors.LIGHT_GREEN_700,
            behavior = ft.SnackBarBehavior.FLOATING,
            action ="Baixar",
            action_color=ft.colors.BLUE_900,
            on_action = event,
            duration = 6000,
            width = int((len(msg)*10)+25) if msg != "Download Disponível" else 330,
            open = True
        )

        self.page.update()


    def warning(self, msg:str) -> SnackBar:

        """ Snackbar para avisar sobre uma ação mau sucedida ou não concluída, ou mesmo um erro do sistema. """

        ICON_SNACK = Icon(name=icons.WARNING_AMBER_ROUNDED, color=ft.colors.BACKGROUND, size=18)
        MSG_SNACK = Text(value=msg, color=ft.colors.BACKGROUND, size=16, weight="w600")

        self.page.snack_bar = SnackBar(
            content = Row(controls=[ICON_SNACK, MSG_SNACK]),
            bgcolor = ft.colors.ERROR,
            behavior= ft.SnackBarBehavior.FLOATING,
            width = int((len(msg)*10)+25),
            open = True
        )

        self.page.update()


    def not_found(self, msg:str) -> SnackBar:

        """ Snackbar para avisar sobre dados não encontrado. """

        ICON_SNACK = Icon(name=icons.SEARCH_OFF_ROUNDED, color=ft.colors.BACKGROUND, size=18)
        MSG_SNACK = Text(value=msg, color=ft.colors.BACKGROUND, size=16, weight="w600")

        self.page.snack_bar = SnackBar(
            content = Row(controls=[ICON_SNACK, MSG_SNACK]),
            bgcolor = ft.colors.INVERSE_SURFACE,
            behavior= ft.SnackBarBehavior.FLOATING,
            width = int((len(msg)*10)+25),
            open = True
        )

        self.page.update()


    def internal_error(self) -> SnackBar:

        """ Snackbar para avisar sobre erros internos do sistema. """

        ICON_SNACK = Icon(name=icons.ERROR_OUTLINE, color=ft.colors.BACKGROUND, size=18)
        MSG_SNACK = Text(value="Erro interno, tente novamente ou contate o suporte.", color=ft.colors.BACKGROUND, size=16, weight="w600")

        self.page.snack_bar = SnackBar(
            content = Row(controls=[ICON_SNACK, MSG_SNACK]),
            bgcolor = ft.colors.INVERSE_SURFACE,
            behavior= ft.SnackBarBehavior.FLOATING,
            width = 455,
            open = True
        )

        self.page.update()

import flet as ft
from flet import ( Page, Ref, Text, TextButton, ButtonStyle, BorderSide, RoundedRectangleBorder, padding )


class ButtonsComponents(TextButton):

    """
    Componente - Padronização de Botões do Sistema
    
    → icon:str = nome do icone flutter.
    → text:str = texto do botão.
    → style = tamanho do botão. Opções disponíveis: "small", "medium" e "default".
    → color = cores do tema. Ex.: "primary", "secondary", etc.
    → data = dados.
    → ref = referenciar o controle.
    → event = evento ao cliclar no botão.

    """

    def __init__(self, page: Page, icon:str=None, text:str="Button", style:str="default", color:str="primary", data=None, ref=Ref, event=None):
        super().__init__()
        self.page = page
        self.icon = icon
        self.text = text
        self.style = ButtonStyle()
        self.data = data
        self.ref = ref
        self.on_click = event


        match style:
            case "small":
                self.style.shape = RoundedRectangleBorder(radius=13)
                self.style.padding = {"": padding.symmetric(vertical=0, horizontal=15)}
            case "medium":
                self.style.shape = RoundedRectangleBorder(radius=10)
                self.style.padding = {"": padding.symmetric(vertical=3, horizontal=20)}
            case _:
                self.style.shape = RoundedRectangleBorder(radius=15)
                self.style.padding = {"": padding.symmetric(vertical=7, horizontal=25)}


        match color:
            case "analog":
                self.select_color = ft.colors.ON_PRIMARY_CONTAINER
                self.secondary_color = ft.colors.ON_PRIMARY_CONTAINER
                self.update
            case "primary":
                self.select_color = ft.colors.PRIMARY
                self.secondary_color = ft.colors.ON_PRIMARY_CONTAINER
                self.update
            case "secondary":
                self.select_color = ft.colors.SECONDARY
                self.secondary_color = ft.colors.INVERSE_PRIMARY
                self.update
            case "info":
                self.select_color = ft.colors.INVERSE_PRIMARY
                self.secondary_color = ft.colors.INVERSE_PRIMARY
                self.update                
            case "success":
                self.select_color = ft.colors.LIGHT_GREEN_ACCENT_700
                self.secondary_color = ft.colors.LIGHT_GREEN_ACCENT_700
                self.update
            case "warning":
                self.select_color = ft.colors.ERROR
                self.secondary_color = ft.colors.ERROR
                self.update
            case "danger":
                self.select_color = ft.colors.ERROR
                self.secondary_color = ft.colors.ERROR
                self.update
            case "light":
                self.select_color = ft.colors.BACKGROUND
                self.secondary_color = ft.colors.BACKGROUND
                self.update
            case "dark":
                self.select_color = ft.colors.ON_BACKGROUND
                self.secondary_color = ft.colors.ON_BACKGROUND
                self.update
            case "bg":
                self.select_color = ft.colors.ON_INVERSE_SURFACE
                self.secondary_color = ft.colors.ON_INVERSE_SURFACE
                self.update
            case "fg":
                self.select_color = ft.colors.ON_INVERSE_SURFACE
                self.secondary_color = ft.colors.ON_INVERSE_SURFACE
                self.update


        self.style.color = ft.colors.BACKGROUND
        self.style.bgcolor = self.select_color
        self.style.bgcolor = {
            "": self.select_color,
            "hovered": self.secondary_color,
        }


    def outline(self):

        self.style.color = {
            "": self.select_color,
        }
        self.style.bgcolor = {
            "": ft.colors.BACKGROUND,
        }
        self.style.side = {
            "hovered": BorderSide(width=1.5, color=self.select_color),
            "": BorderSide(width=1, color=ft.colors.BACKGROUND),
        }
        self.update
        return self

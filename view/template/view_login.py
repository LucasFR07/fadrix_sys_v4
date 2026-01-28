from flet import ( Page, View, MainAxisAlignment, CrossAxisAlignment, padding, colors )

## VIEWS TEMPLATE
from view.template.login import UserLogin


class ViewLogin(View):

    def __init__(self, page:Page):
        super().__init__()
        self.page = page

        self.appbar = None
        self.navigation_bar = None
        self.controls = [UserLogin(self.page)]
        self.bgcolor = colors.SURFACE_VARIANT
        self.horizontal_alignment = CrossAxisAlignment.CENTER
        self.vertical_alignment = MainAxisAlignment.CENTER
        self.padding = padding.all(0)

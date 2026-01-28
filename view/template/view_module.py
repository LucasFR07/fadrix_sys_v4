import flet as ft
from flet import ( Page, View, Container, Row, margin, padding )

## CONTROLES DO SISTEMA
from controllers.date_control import date_create as DATE
from controllers.user_control import UserControl

## TEMPLATE
from view.template.appbar import AppBar

## MODULOS TEMPLATE
from view.modules.order.order_list import OrderList
from view.modules.order.order_import import OrderImport
from view.modules.order.order_view import OrderView
from view.modules.warranty.w_list import WarrantyList
from view.modules.warranty.w_new import NewWarranty

class ViewModule(View):

    def __init__(self, page:Page, module:str):
        super().__init__()
        self.page = page

        ## OBTER DADOS DO USUÁRIO CONECTADO
        self.user_system = self.page.client_storage.get("user_info")
        self.page.theme = ft.Theme(color_scheme_seed=self.user_system["theme_color"])
        self.page.theme_mode = self.user_system["theme_light"]

        self.navigation_drawer_index = self.page.session.get("navigation_drawer_index")
        ## ---------

        self.module = module
        self.appbar = AppBar(self.page, user=self.user_system, drawer=self.show_drawer)
        self.controls = self.__create_controls()
        self.padding = padding.all(0)

        if self.user_system["usr_group"] in ["Administrador", 'Vendas']:
            self.drawer = ft.NavigationDrawer(
                controls=[
                    ft.Container(
                        content=Row(
                            controls=[
                                ft.CircleAvatar(
                                    foreground_image_url=f'https://avatar.skype.com/v1/avatars/{self.user_system["photo_skype"]}?auth_key=39969709&size=m',
                                    content=ft.Text(value=f''.join([x[0].upper() for x in self.user_system["name"].split(maxsplit=1)]), color=ft.colors.ON_BACKGROUND),
                                    bgcolor=ft.colors.ERROR,
                                    radius=20,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(value=self.user_system["name"], color=ft.colors.BACKGROUND, weight=ft.FontWeight.W_700, size=16),
                                        ft.Text(value=self.user_system["user"], color=ft.colors.BACKGROUND, weight=ft.FontWeight.W_300, size=12)
                                    ],
                                    spacing=0
                                ),
                                ft.IconButton(icon=ft.icons.LOGOUT, icon_color=ft.colors.BACKGROUND, on_click=self.__logout)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15
                        ),
                        bgcolor=ft.colors.PRIMARY,
                        padding=padding.symmetric(20, 25),
                        margin=margin.only(bottom=20)
                    ),
                    ft.NavigationDrawerDestination(
                        icon_content=ft.Icon(ft.icons.SHOPPING_CART_OUTLINED),
                        label="Pedidos",
                        selected_icon=ft.icons.SHOPPING_CART,
                    ),
                    ft.NavigationDrawerDestination(
                        icon_content=ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINED),
                        label="Garantias (beta)",
                        selected_icon=ft.icons.CHECK_CIRCLE,
                    ),
                    # ft.NavigationDrawerDestination(
                    #     icon_content=ft.Icon(ft.icons.LOCAL_SHIPPING_OUTLINED),
                    #     label="Cotação Frete",
                    #     selected_icon=ft.icons.LOCAL_SHIPPING,
                    # ),
                    # ft.NavigationDrawerDestination(
                    #     icon_content=ft.Icon(ft.icons.SETTINGS_APPLICATIONS_OUTLINED),
                    #     label="Configurações",
                    #     selected_icon=ft.icons.SETTINGS_APPLICATIONS,
                    # ),                
                    ft.Container(margin=margin.symmetric(vertical=50))
                ],
                selected_index=self.navigation_drawer_index,
                indicator_color=ft.colors.INVERSE_PRIMARY,
                indicator_shape=ft.RoundedRectangleBorder(radius=10),
                tile_padding=padding.symmetric(vertical=5, horizontal=20),
                bgcolor=ft.colors.BACKGROUND,
                on_change=self.change_drawer
            )

        else:
            self.drawer = ft.NavigationDrawer(
                controls=[
                    ft.Container(
                        content=Row(
                            controls=[
                                ft.CircleAvatar(
                                    foreground_image_url=f'https://avatar.skype.com/v1/avatars/{self.user_system["photo_skype"]}?auth_key=39969709&size=m',
                                    content=ft.Text(value=f''.join([x[0].upper() for x in self.user_system["name"].split(maxsplit=1)]), color=ft.colors.ON_BACKGROUND),
                                    bgcolor=ft.colors.ERROR,
                                    radius=20,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(value=self.user_system["name"], color=ft.colors.BACKGROUND, weight=ft.FontWeight.W_700, size=16),
                                        ft.Text(value=self.user_system["user"], color=ft.colors.BACKGROUND, weight=ft.FontWeight.W_300, size=12)
                                    ],
                                    spacing=0
                                ),
                                ft.IconButton(icon=ft.icons.LOGOUT, icon_color=ft.colors.BACKGROUND, on_click=self.__logout)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15
                        ),
                        bgcolor=ft.colors.PRIMARY,
                        padding=padding.symmetric(20, 25),
                        margin=margin.only(bottom=20)
                    ),
                    ft.NavigationDrawerDestination(
                        icon_content=ft.Icon(ft.icons.SHOPPING_CART_OUTLINED),
                        label="Pedidos",
                        selected_icon=ft.icons.SHOPPING_CART,
                    ),
                    # ft.NavigationDrawerDestination(
                    #     icon_content=ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINED),
                    #     label="Garantias",
                    #     selected_icon=ft.icons.CHECK_CIRCLE,
                    # ),
                    # ft.NavigationDrawerDestination(
                    #     icon_content=ft.Icon(ft.icons.LOCAL_SHIPPING_OUTLINED),
                    #     label="Cotação Frete",
                    #     selected_icon=ft.icons.LOCAL_SHIPPING,
                    # ),
                    # ft.NavigationDrawerDestination(
                    #     icon_content=ft.Icon(ft.icons.SETTINGS_APPLICATIONS_OUTLINED),
                    #     label="Configurações",
                    #     selected_icon=ft.icons.SETTINGS_APPLICATIONS,
                    # ),                
                    ft.Container(margin=margin.symmetric(vertical=50))
                ],
                selected_index=self.navigation_drawer_index,
                indicator_color=ft.colors.INVERSE_PRIMARY,
                indicator_shape=ft.RoundedRectangleBorder(radius=10),
                tile_padding=padding.symmetric(vertical=5, horizontal=20),
                bgcolor=ft.colors.BACKGROUND,
                on_change=self.change_drawer
            )


    def __create_controls(self):

        """ Cria a estrutura da página. """

        return [
            Container(
                content=Row(
                    controls=[
                        Container(),
                        Container(
                            content=self.__get_module(),
                            expand=True
                        )
                    ],
                    spacing=0
                ),
                bgcolor=ft.colors.SURFACE_VARIANT,
                margin=margin.all(0),
                padding=padding.all(0),
                expand=True
            ),
        ]


    def __get_module(self):

        """ Define a página a ser exibida de acordo com o parâmetro informado. """

        match self.module:
            case "order_list":
                try:
                    return OrderList(self.page)
                except Exception as exc:
                    print(f'\n[ERRO] VIEW_MODULE > __get_module(order_list) ==> EXCEPTION: {exc}\n')
                    import traceback
                    traceback.print_exc()
                    return Container(content=Text(f"Erro ao carregar módulo: {exc}"))
            case "order_view":
                return OrderView(self.page)
            case "order_import":
                return OrderImport(self.page)
            case "w_list":
                return WarrantyList(self.page)
            case "w_new":
                return NewWarranty(self.page)


    def show_drawer(self, e):
        self.drawer.open = True
        self.drawer.update()


    def change_drawer(self, e):

        self.page.session.set("navigation_drawer_index", e.control.selected_index)
        match e.control.selected_index:

            case 0:
                self.page.go("/pedidos")

            case 1:
                self.page.go("/garantias")


    def __logout(self, e):

        """ Logout da conta do usuário. """

        self.page.client_storage.clear()
        UserControl().logout(self.user_system["id"])
        print(f'[LOGOUT] NOVO LOGOUT = Usuario {self.user_system["user"]}, fez logout em {DATE().strftime("%d/%m/%Y %H:%M:%S")}') #DEBUG
        self.page.go("/")

import flet as ft
from flet import ( Page, UserControl, Text, ButtonStyle, CircleBorder, Row, Container, ElevatedButton, Icon, icons)


class Pagination(UserControl):

    def __init__(self, page:Page):
        super().__init__()
        self.page = page
        self.view_pagination = Row(spacing=1)


    def create_pagination(self, max_page:int, curr_page:int, index:int, funcNum, funcLast, funcNext):

        self.max_page = max_page
        self.curr_page = curr_page
        self.index = index
        self.action_number_page = funcNum
        self.action_last = funcLast
        self.action_next = funcNext

        self.view_pagination.controls.append(
            ElevatedButton(
                content=Icon(icons.KEYBOARD_ARROW_LEFT),
                width=30,
                height=30,
                style=ButtonStyle(
                    color={
                        "hovered": ft.colors.BACKGROUND,
                        "": ft.colors.PRIMARY,
                    },                        
                    bgcolor={
                        "hovered": ft.colors.PRIMARY,
                        "": ft.colors.BACKGROUND,
                    },
                    overlay_color=None,
                    shape=CircleBorder(),
                    padding=0,
                ),
                on_click=self.action_last
            )            
        )

        sum = self.index//2    
        if int(self.curr_page) < (self.index):
            for page in range(1,self.index+1):
                if page == self.curr_page:
                    self.view_pagination.controls.append(
                        ElevatedButton(
                            text=page,
                            style=ButtonStyle(
                                color=ft.colors.BACKGROUND,                        
                                bgcolor=ft.colors.PRIMARY,
                                overlay_color=None,
                                shape=CircleBorder(),
                                padding=0,
                            ),
                            data=page,
                            on_click=self.action_number_page,
                        )
                    )                    
                else:
                    self.view_pagination.controls.append(
                        ElevatedButton(
                            text=page,
                            style=ButtonStyle(
                                color={
                                    "hovered": ft.colors.BACKGROUND,
                                    "": ft.colors.PRIMARY,
                                },                        
                                bgcolor={
                                    "hovered": ft.colors.PRIMARY,
                                    "": ft.colors.BACKGROUND,
                                },
                                overlay_color=None,
                                shape=CircleBorder(),
                                padding=0,
                            ),
                            data=page,
                            on_click=self.action_number_page,
                        )
                    )

        elif self.curr_page > (self.max_page - self.index):
            for page in range((self.max_page+1)-self.index, self.max_page+1):
                if page == self.curr_page:
                    self.view_pagination.controls.append(
                        ElevatedButton(
                            text=page,
                            style=ButtonStyle(
                                color=ft.colors.BACKGROUND,                        
                                bgcolor=ft.colors.PRIMARY,
                                overlay_color=None,
                                shape=CircleBorder(),
                                padding=0,
                            ),
                            data=page,
                            on_click=self.action_number_page,
                        )
                    )
                else:
                    self.view_pagination.controls.append(
                        ElevatedButton(
                            text=page,
                            style=ButtonStyle(
                                color={
                                    "hovered": ft.colors.BACKGROUND,
                                    "": ft.colors.PRIMARY,
                                },                        
                                bgcolor={
                                    "hovered": ft.colors.PRIMARY,
                                    "": ft.colors.BACKGROUND,
                                },
                                overlay_color=None,
                                shape=CircleBorder(),
                                padding=0,
                            ),
                            data=page,
                            on_click=self.action_number_page,
                        )
                    )

        else:
            if self.index%2 == 0:
                for page in range(self.curr_page-sum,self.curr_page+sum):
                    if page == self.curr_page:
                        self.view_pagination.controls.append(
                            ElevatedButton(
                                text=page,
                                style=ButtonStyle(
                                    color=ft.colors.BACKGROUND,                        
                                    bgcolor=ft.colors.PRIMARY,
                                    overlay_color=None,
                                    shape=CircleBorder(),
                                    padding=0,
                                ),
                                data=page,
                                on_click=self.action_number_page,
                            )
                        )
                    else:
                        self.view_pagination.controls.append(
                            ElevatedButton(
                                text=page,
                                style=ButtonStyle(
                                    color={
                                        "hovered": ft.colors.BACKGROUND,
                                        "": ft.colors.PRIMARY,
                                    },                        
                                    bgcolor={
                                        "hovered": ft.colors.PRIMARY,
                                        "": ft.colors.BACKGROUND,
                                    },
                                    overlay_color=None,
                                    shape=CircleBorder(),
                                    padding=0,
                                ),
                                data=page,
                                on_click=self.action_number_page,
                            )
                        )

            else:
                for page in range(self.curr_page-sum,self.curr_page+sum+1):
                    if page == self.curr_page:
                        self.view_pagination.controls.append(
                            ElevatedButton(
                                text=page,
                                style=ButtonStyle(
                                    color=ft.colors.BACKGROUND,                        
                                    bgcolor=ft.colors.PRIMARY,
                                    overlay_color=None,
                                    shape=CircleBorder(),
                                    padding=0,
                                ),
                                data=page,
                                on_click=self.action_number_page,
                            )
                        )
                    else:
                        self.view_pagination.controls.append(
                            ElevatedButton(
                                text=page,
                                style=ButtonStyle(
                                    color={
                                        "hovered": ft.colors.BACKGROUND,
                                        "": ft.colors.PRIMARY,
                                    },                        
                                    bgcolor={
                                        "hovered": ft.colors.PRIMARY,
                                        "": ft.colors.BACKGROUND,
                                    },
                                    overlay_color=None,
                                    shape=CircleBorder(),
                                    padding=0,
                                ),
                                data=page,
                                on_click=self.action_number_page,
                            )
                        )

        self.view_pagination.controls.append(
            ElevatedButton(
                content=Icon(icons.KEYBOARD_ARROW_RIGHT),
                width=30,
                height=30,
                style=ButtonStyle(
                    color={
                        "hovered": ft.colors.BACKGROUND,
                        "": ft.colors.PRIMARY,
                    },                        
                    bgcolor={
                        "hovered": ft.colors.PRIMARY,
                        "": ft.colors.BACKGROUND,
                    },
                    overlay_color=None,
                    shape=CircleBorder(),
                    padding=0,
                ),
                on_click=self.action_next
            )            
        )

        self.update()


    def build(self):
        self.view = Container(
            content=Row(
                [
                    Text("voltar", size=12, color=ft.colors.PRIMARY),
                    self.view_pagination,
                    Text("avançar", size=12, color=ft.colors.PRIMARY),                     
                ]
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
        )

        return self.view

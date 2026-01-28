import flet as ft
from flet import (
    Page, AlertDialog, GridView, Column, Row, Container,
    Text, Icon, IconButton, MainAxisAlignment, RoundedRectangleBorder,
    icons, padding, margin, alignment, border_radius, border
)


## Controles do Sistema
import calendar
from controllers.date_control import date_create as DATE


class Calendar(AlertDialog):
    
    def __init__(self, page: Page, func):
        super().__init__()
        self.page = page 
        self.func_select = func

        self.calendar = calendar
        self.calendar.setfirstweekday(calendar.SUNDAY)

        self.modal = False
        self.title_padding = padding.all(0)
        self.content = Container(content=self.create_calendar(), height=395)
        self.content_padding = padding.symmetric(vertical=15, horizontal=15)
        self.shape = RoundedRectangleBorder(radius=10)
        self.actions_padding = padding.all(0)
        self.on_dismiss = self.dismiss



    def create_calendar(self, y=None, m=None):

        self.current_year = DATE().year if y == None else y
        self.current_month = DATE().month if m == None else m
        self.today = f'{DATE().day}/{DATE().month}/{DATE().year}'
        month_matrix = self.calendar.monthcalendar(year=self.current_year, month=self.current_month)

        week_content = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
        month_content = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        self.calendar_content = GridView(
            expand=1,
            width=300,
            runs_count=10,
            max_extent=40,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
        )

        for week_name in week_content:
            self.calendar_content.controls.append(
                Container(
                    content=Text(value=week_name, color=ft.colors.ON_BACKGROUND, text_align="center", weight="w500"),
                    alignment=alignment.center
                )
            )

        for week in month_matrix:
            for index, day in enumerate(week):
                if f'{day}/{self.current_month}/{self.current_year}' == self.today:
                    self.calendar_content.controls.append(
                        Container(
                            content=Text(value=day, color=ft.colors.ON_BACKGROUND, text_align="center"),
                            bgcolor=ft.colors.OUTLINE_VARIANT if index == 0 or index == 6 else ft.colors.BACKGROUND,
                            border=border.all(1.5, ft.colors.PRIMARY),
                            border_radius=5,
                            data={"day": day, "month": self.current_month, "year": self.current_year, "index": index},
                            alignment=alignment.center,
                            on_hover=self.hover_date,
                            on_click=self.func_select
                        )
                    )
                elif day != 0:
                    self.calendar_content.controls.append(
                        Container(
                            content=Text(value=day, color=ft.colors.ON_BACKGROUND, text_align="center"),
                            bgcolor=ft.colors.OUTLINE_VARIANT if index == 0 or index == 6 else ft.colors.BACKGROUND,
                            border_radius=5,
                            data={"day": day, "month": self.current_month, "year": self.current_year, "index": index},
                            alignment=alignment.center,
                            on_hover=self.hover_date,
                            on_click=self.func_select
                        )
                    )
                else:
                    self.calendar_content.controls.append(
                        Container(
                            content=Text(value="", color=ft.colors.ON_BACKGROUND, text_align="center"),
                            alignment=alignment.center
                        )
                    )

        self.view = Column(
            controls=[
                Container(
                    bgcolor=ft.colors.PRIMARY,
                    height=43,
                    border_radius=border_radius.all(5),
                    content=Row(
                        controls=[
                            Icon(name=icons.CALENDAR_TODAY, color=ft.colors.BACKGROUND, size=18),
                            Text(value="SELECIONAR DATA", color=ft.colors.BACKGROUND, size=16, weight="w500"),
                        ],
                        alignment=MainAxisAlignment.CENTER
                    ),
                    alignment=alignment.center,
                    margin=margin.only(bottom=10)
                ),
                Row(
                    controls=[
                        IconButton(
                            icon=icons.KEYBOARD_ARROW_LEFT,
                            icon_color=ft.colors.PRIMARY,
                            data=self.current_month,
                            on_click=self.last_month
                        ),
                        Text(value=f'{month_content[(self.current_month)-1]} {self.current_year}', size=18, weight="w700", color=ft.colors.ON_BACKGROUND),
                        IconButton(
                            icon=icons.KEYBOARD_ARROW_RIGHT,
                            icon_color=ft.colors.PRIMARY,
                            data=self.current_month,
                            on_click=self.next_month
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN
                ),
                self.calendar_content
            ],
            spacing=30,
            alignment=MainAxisAlignment.SPACE_AROUND
        )

        return self.view


    def hover_date(self, e):
        index = e.control.data["index"]
        self.background = ft.colors.OUTLINE_VARIANT if index == 0 or index == 6 else ft.colors.BACKGROUND
        e.control.content.color = ft.colors.BACKGROUND if e.data == "true" else ft.colors.ON_BACKGROUND
        e.control.bgcolor = ft.colors.PRIMARY if e.data == "true" else self.background
        self.update()
        self.page.update()


    def dismiss(self, e):
        self.current_year = DATE().year
        self.current_month = DATE().month
        self.update()
        self.content = Container(content=self.create_calendar(), height=395)


    def close_dialog(self):
        self.open = False
        self.current_year = DATE().year
        self.current_month = DATE().month
        self.content = Container(content=self.create_calendar(), height=395)


    def next_month(self, e):
        if e.control.data == 12:
            next_month = 1
            next_year = self.current_year + 1
        else:
            next_month = self.current_month + 1
            next_year = self.current_year

        self.content = Container(content=self.create_calendar(y=next_year, m= next_month), height=395)
        self.update()


    def last_month(self, e):
        if e.control.data == 1:
            last_month = 12
            last_year = self.current_year - 1
        else:
            last_month = self.current_month - 1
            last_year = self.current_year

        self.content = Container(content=self.create_calendar(y=last_year, m= last_month), height=395)
        self.update()

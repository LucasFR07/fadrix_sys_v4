from flet import ( Page, UserControl, Container, Column, Row, PopupMenuItem, ListTile, Text, Icon, FontWeight, TextOverflow, MainAxisAlignment, colors, icons, border_radius, padding )
from datetime import datetime

## CONEXÃO COM DADOS
from data.repository.notice import NoticeRepository as NOTICE
from sqlalchemy import null

## COMPONENTES TEMPLATE
from view.component.buttons import ButtonsComponents as BTN
from view.component.dialog import Dialog
from view.component.snackbar import SnackBar_PATTERNS


class NoticeControl(UserControl):

    def __init__(self, page:Page, topic:str, title:str, messagem:str, action:str, user:str, link:str=None, date:datetime=None) -> None:

        self.page=page
        self.date=date if date != None else datetime.now()
        self.topic=topic
        self.title=title
        self.messagem=messagem
        self.action=action
        self.link=link if link != None else null()
        self.user=user

        ## WIDGETS:
        self.alert = Dialog(self.page)
        self.snackbar = SnackBar_PATTERNS(self.page)
        ## ---------


    def create_notice(self) -> bool:

        """ Cria uma nova notificação no banco de dados. """

        try:
            NOTICE().insert(
                date=self.date,
                user=self.user,
                topic=self.topic,
                title=self.title,
                messagem=self.messagem,
                action=self.action,
                link=self.link
            )
            return True

        except Exception as exc:
            print(f'\n❌ NOTICE_CONTROL > create_notice() == EXCEPTION: {exc}\n')
            return False


    def return_notice(self) -> PopupMenuItem:

        """ Retorna as notificações do sistema para listagem na caixa de notificação. """

        notice_item = PopupMenuItem(
            content=ListTile(
                title=Text(value=self.title, size=14, color=colors.ON_BACKGROUND, weight=FontWeight.W_700),
                subtitle=Column(
                    controls=[
                        Text(value=f'{self.messagem[0:90]}\n\nSAIBA MAIS ...' if self.action == "Diálogo" else self.messagem[0:90], size=12, color=colors.ON_BACKGROUND, weight=FontWeight.W_400),
                        Text(value=f'{self.user}, {self.date.strftime('%d/%m/%Y %H:%M:%S')}', size=9, color=colors.OUTLINE, italic=True)
                    ]
                ),
            )
        )

        match self.action:

            case "Download":
                notice_item.content.leading = Icon(icons.DOWNLOAD)
                notice_item.on_click = lambda e: self.page.launch_url(url=f'http://192.168.1.35:62024/{self.link}')
                return notice_item

            case "Diálogo":
                notice_item.content.leading = Icon(icons.UPDATE)
                notice_item.data = {"icon": icons.UPDATE}
                notice_item.on_click = self.__notice_dialog
                return notice_item


    def __notice_dialog(self, e) -> None:

        icon_box = e.control.data["icon"]

        self.alert.default_dialog(
            title=Container(
                content=Row(
                    controls=[
                        Icon(name=icon_box, color=colors.ON_BACKGROUND),
                        Text(value=self.title.upper(), size=18, weight=FontWeight.W_600, color=colors.ON_BACKGROUND)
                    ],
                    alignment=MainAxisAlignment.START
                ),
                bgcolor=colors.SURFACE_VARIANT,
                border_radius=border_radius.all(5),
                padding=padding.symmetric(15,10)
            ),
            contt=Text(value=self.messagem, size=16, weight=FontWeight.W_300, color=colors.ON_BACKGROUND),
            act=[]
        )

        self.page.dialog=self.alert
        self.alert.open=True
        self.page.update()
        return None

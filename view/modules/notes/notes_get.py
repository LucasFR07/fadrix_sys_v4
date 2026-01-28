import flet as ft
from data.repository.commentsV2 import CommentsV2Repository as NOTE
from pathlib import Path



class NotesGet:

    def __init__(self, page:ft.Page, set_module:str, set_reference:str, set_user:str, set_systemnote:str=None) -> None:

        self.page = page
        self.set_module = set_module
        self.set_reference = set_reference
        self.set_user = set_user
        self.set_systemnote = set_systemnote


    def __get_notes(self):
        """ Busca as anotações cadastradas no sistema para cada módulo e referência (pedido, garantia, etc.). """

        try:
            search_notes = NOTE().filter_reference(self.set_module, self.set_reference)
            return search_notes

        except Exception as exc:
            print(f'\n❌ NOTESGET > __get_notes() == EXCEPTION: {exc}\n')
            return None


    def __get_system_note(self)  -> (ft.ListTile | None):
        """ Cria o comentário padrão do sistema, caso haja. """

        try:
            if self.set_systemnote != None:
                return ft.ListTile(
                    leading=ft.CircleAvatar(
                        foreground_image_url='assets/images/profile/profile_default.png',
                        content=ft.Text(value=f'SYS', color=ft.colors.ON_BACKGROUND, size=11),
                        bgcolor=ft.colors.with_opacity(0.5, ft.colors.SURFACE_VARIANT),
                        radius=15
                    ),
                    title=ft.Container(
                        content=ft.Text(value=self.set_systemnote, size=13, color=ft.colors.ON_BACKGROUND, selectable=True),
                        bgcolor=ft.colors.with_opacity(0.5, ft.colors.TERTIARY_CONTAINER),
                        border_radius=ft.border_radius.all(10),
                        padding=ft.padding.symmetric(10,7)
                    ),
                    subtitle=ft.Text(value='Fadrix SYSTEM', size=11, color=ft.colors.ON_BACKGROUND)
                )

            else:
                return None

        except Exception as exc:
            print(f'\n❌ NOTESGET > __system_note() == EXCEPTION: {exc}\n')
            return None


    def set_notes(self) -> list:
        """ Lista todas as notas criada para o módulo e referência informada. """

        try:
            set_notes = self.__get_notes()
            set_system_note = self.__get_system_note()
            list_notes = list()

            if set_system_note != None:
                list_notes.append(set_system_note)

            if set_notes != None:
                for note in set_notes:

                    match note.type_msg:

                        case "text":
                            content_type = ft.Container(
                                content=ft.Text(value=note.text, size=13, color=ft.colors.ON_BACKGROUND, selectable=True),
                                bgcolor=ft.colors.with_opacity(0.5, ft.colors.SECONDARY_CONTAINER),
                                border_radius=ft.border_radius.all(10),
                                padding=ft.padding.symmetric(10,7)
                            )
                            width_type = 900

                        case "image":
                            content_type = ft.Container(
                                content=ft.Container(content=ft.Image(src=note.image, height=120), data=note.image, ink=True, on_click=self.event_image_type),
                                border_radius=ft.border_radius.all(10),
                                padding=ft.padding.symmetric(10,7),
                                alignment=ft.alignment.top_left
                            )
                            width_type = 300

                        case "attachment":
                            file_attachment = Path(f'V4\\{note.attachment}')
                            content_type = ft.Container(
                                content=ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Image(
                                                src=f'assets/images/system/{file_attachment.suffix.replace('.', '')}.png',
                                                error_content=ft.Image(src='assets/images/system/file.png', height=40),
                                                height=40
                                            ),
                                            ft.Column(
                                                controls=[
                                                    ft.Text(value=file_attachment.name, color=ft.colors.ON_BACKGROUND, size=14, weight="w500", width=300, no_wrap=False),
                                                    ft.Text(value=f'{file_attachment.stat().st_size} KB', color=ft.colors.ON_BACKGROUND, size=12, weight="w300")
                                                ],
                                                spacing=2
                                            ),
                                            ft.IconButton(icon=ft.icons.DOWNLOAD_ROUNDED, bgcolor=ft.colors.SECONDARY_CONTAINER, data=note.attachment, on_click=self.event_attachment_type)
                                        ],
                                        spacing=10,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                                    )
                                ),
                                bgcolor=ft.colors.with_opacity(0.5, ft.colors.SECONDARY_CONTAINER),
                                border_radius=ft.border_radius.all(10),
                                padding=ft.padding.symmetric(10,7)
                            )
                            width_type = 600

                    list_notes.append(
                        ft.ListTile(
                            leading = ft.CircleAvatar(
                                foreground_image_url='assets/images/profile/profile_default.png',
                                content=ft.Text(value=f''.join([x[0].upper() for x in note.user.split(maxsplit=1)]), color=ft.colors.ON_BACKGROUND),
                                bgcolor=ft.colors.with_opacity(0.5, ft.colors.SURFACE_VARIANT),
                                radius=15
                            ),
                            title=content_type,
                            subtitle=ft.Text(value=f'{note.user}, {note.date.strftime('%d/%m/%Y %H:%M:%S')}', size=11, color=ft.colors.ON_BACKGROUND),
                            trailing=ft.IconButton(icon=ft.icons.MORE_VERT),
                            width=width_type
                        )
                    )

            return list_notes

        except Exception as exc:
            print(f'\n❌ NOTESGET > __set_notes() == EXCEPTION: {exc}\n')
            return list_notes



    ## EVENTOS DO SISTEMA ------

    def event_image_type(self, e):
        """ Evento para capturar comando do usuário para abrir a foto em tela. """

        try:
            expand_image = ft.AlertDialog(
                title=None,
                title_padding=ft.padding.all(0),
                content=ft.Container(content=ft.Image(src=e.control.data), height=700),
                content_padding=ft.padding.symmetric(5,5),
                actions=None,
                actions_padding=ft.padding.all(0),
                shape=ft.RoundedRectangleBorder(radius=5),
                adaptive=True
            )

            self.page.dialog = expand_image
            expand_image.open = True
            self.page.update()

        except Exception as exc:
            print(f'\n❌ NOTESGET > event_image_type() == EXCEPTION: {exc}\n')
            return None


    def event_attachment_type(self, e):
        """ Evento para capturar o comando do usuário de baixar o arquivo anexado. """

        try:
            print(f'\n⬇️ NOTESGET > event_attachment_type() == DOWNLOAD ATTACHMENT: {e.control.data}, por {self.set_user}\n')
            self.page.launch_url(url=f'http://192.168.1.35:62024/{e.control.data}')

        except Exception as exc:
            print(f'\n❌ NOTESGET > event_attachment_type() == EXCEPTION: {exc}\n')

    ## ------

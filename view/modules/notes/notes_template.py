import flet as ft
from data.repository.commentsV2 import CommentsV2Repository as NOTE
from sqlalchemy import null

from view.modules.notes.notes_get import NotesGet
from view.component.snackbar import SnackBar_PATTERNS
from source.api.asanaApi import AsanaAPI
from controllers.date_control import date_create as DATE
from pathlib import Path
import shutil, os



class NotesTemplate(NotesGet):

    def __init__(self, page:ft.Page, set_module:str, set_reference:str, set_user:str, task_ids:str, set_systemnote:str=None) -> None:
        super().__init__(page, set_module, set_reference, set_user, set_systemnote)

        self.task_ids = task_ids
        self.snackbar = SnackBar_PATTERNS(self.page)

        ## REFERENCIAS ------
        self.set_note_text = ft.Ref[ft.TextField]()
        self.check_asana = ft.Ref[ft.Switch]()
        ## ------

        self.image_file = ft.FilePicker(on_result=self.__insert_image_result, on_upload=self.__insert_image_progress)
        self.page.overlay.append(self.image_file)

        self.attachment_file = ft.FilePicker(on_result=self.__insert_attachment_result, on_upload=self.__insert_attachment_progress)
        self.page.overlay.append(self.attachment_file)


    def create_template(self) -> ft.Column:
        """ Cria o template para ser exibido para os usuários. """

        try:
            notes = self.set_notes()

            self.set_box_notes = ft.Container(
                content=ft.Column(
                    controls=notes,
                    alignment=ft.MainAxisAlignment.END,
                    scroll=ft.ScrollMode.AUTO,
                    auto_scroll=True
                ),
                padding=ft.padding.symmetric(vertical=15),
                alignment=ft.alignment.bottom_left,
                height=300
            )

            self.set_box_actions = ft.Container(
                content=ft.Row(

                    controls=[

                        ft.TextField(
                            value=None,
                            ref=self.set_note_text,
                            text_style=ft.TextStyle(size=16, weight="w400"),
                            color=ft.colors.ON_BACKGROUND,
                            bgcolor=ft.colors.with_opacity(0.5, ft.colors.SURFACE_VARIANT),
                            border_color=ft.colors.with_opacity(0.5, ft.colors.SURFACE_VARIANT),
                            border_radius=15,
                            hint_text="Digite aqui",
                            hint_style=ft.TextStyle(size=13, weight="w300"),
                            focused_color=ft.colors.ON_BACKGROUND,
                            content_padding=ft.padding.symmetric(vertical=5, horizontal=20),
                            shift_enter=True,
                            max_lines=3,
                            expand=True,
                            on_submit=self.__insert_text
                        ),

                        ft.IconButton(
                            icon=ft.icons.IMAGE_OUTLINED,
                            bgcolor=ft.colors.with_opacity(0.5, ft.colors.SURFACE_VARIANT),
                            tooltip="Anexar imagem",
                            on_click=lambda _: self.image_file.pick_files(
                                dialog_title="Escolher imagem",
                                initial_directory="/Desktop",
                                file_type=ft.FilePickerFileType.IMAGE,
                                allow_multiple=False
                            )
                        ),

                        ft.IconButton(
                            icon=ft.icons.ATTACH_FILE_ROUNDED,
                            bgcolor=ft.colors.with_opacity(0.5, ft.colors.SURFACE_VARIANT),
                            tooltip="Adicionar anexos",
                            on_click=lambda _: self.attachment_file.pick_files(
                                dialog_title="Escolher arquivo",
                                initial_directory="/Desktop",
                                file_type=ft.FilePickerFileType.CUSTOM,
                                allowed_extensions=['pdf', 'psd', 'cdr', 'ai', 'zip', 'rar', 'xls', 'xlsx', 'txt', 'docx'],
                                allow_multiple=False
                            )
                        ),

                        ft.Switch(width=80, tooltip="Enviar comentário para Asana", ref=self.check_asana)

                    ]
                ),
                alignment=ft.alignment.center_left
            )

            return ft.Column(controls=[self.set_box_notes, self.set_box_actions])

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > create_template() == EXCEPTION: {exc}\n')
            self.snackbar.internal_error()
            self.page.update()


    ## AÇÕES DE NOTAS ------

    def __insert_DB(self, date_msg, type_msg:str, msg:str) -> bool:
        """ Inseri o comentário no banco de dados do sistema. """

        try:
            NOTE().insert(
                sign = null(),
                module = self.set_module,
                reference = self.set_reference,
                user = self.set_user,
                date = date_msg,
                type_msg = type_msg,
                text = msg if type_msg == "text" else null(),
                sticker = msg if type_msg == "sticker" else null(),
                image = msg if type_msg == "image" else null(),
                audio = msg if type_msg == "audio" else null(),
                video = msg if type_msg == "video" else null(),
                attachment = msg if type_msg == "attachment" else null(),
                reply = null()
            )
            return True

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_DB) == EXCEPTION INSERT DB: {exc}\n')
            self.snackbar.warning("Não foi possível adicionar o comentário ao sistema. Tente novamente ou contate o suporte.")            
            return False


    def __insert_note(self, date_msg, type_msg:str, msg:str) -> None:
        """ Inseri o novo comentário no chat para o usuário visualizar. """

        try:
            
            match type_msg:

                case "text":
                    content_type = ft.Container(
                        content=ft.Text(value=msg, size=13, color=ft.colors.ON_BACKGROUND, selectable=True),
                        bgcolor=ft.colors.with_opacity(0.5, ft.colors.SECONDARY_CONTAINER),
                        border_radius=ft.border_radius.all(10),
                        padding=ft.padding.symmetric(10,7)
                    )
                    width_type = 900

                case "image":
                    file_attachment = Path(msg)
                    content_type = ft.Container(
                        content=ft.Container(content=ft.Image(src=file_attachment, height=120), data=file_attachment, ink=True, on_click=self.event_image_type),
                        border_radius=ft.border_radius.all(10),
                        padding=ft.padding.symmetric(10,7),
                        alignment=ft.alignment.top_left
                    )
                    width_type = 300

                case "attachment":
                    file_attachment = Path(f'V4\\{msg}')
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
                                    ft.IconButton(icon=ft.icons.DOWNLOAD_ROUNDED, bgcolor=ft.colors.SECONDARY_CONTAINER, data=file_attachment, on_click=self.event_attachment_type)
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

            self.set_box_notes.content.controls.append(
                ft.ListTile(
                    leading = ft.CircleAvatar(
                        foreground_image_url='assets/images/profile/profile_default.png',
                        content=ft.Text(value=f''.join([x[0].upper() for x in self.set_user.split(maxsplit=1)]), color=ft.colors.ON_BACKGROUND),
                        bgcolor=ft.colors.with_opacity(0.5, ft.colors.SURFACE_VARIANT),
                        radius=15
                    ),
                    title=content_type,
                    subtitle=ft.Text(value=f'{self.set_user}, {date_msg.strftime('%d/%m/%Y %H:%M:%S')}', size=11, color=ft.colors.ON_BACKGROUND),
                    trailing=ft.IconButton(icon=ft.icons.MORE_VERT),
                    width=width_type
                )
            )

            self.set_box_notes.content.update()
            self.page.update()

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_note() == EXCEPTION INSERT NOTE: {exc}\n') ##DEBUG
            self.snackbar.warning("Não foi possível exibir o novo comentário na conversa. Atualize a página ou tente novamente.")
            self.page.update()


    def __insert_asana(self, type_msg:str, msg:str=None, file_name:str=None) -> None:
        """ Envia o comentário para a tarefa correspondente no Asana. """

        try:
            if self.check_asana.current.value:

                ASANA = AsanaAPI()
                for key, value in self.task_ids.items():

                    match isinstance(value, str):
                        case True:
                            id_task = value
                        case False:
                            for gid in value:
                                id_task = gid

                    match type_msg:

                        case "text":
                            ASANA.stories(
                                text=f'<strong>{self.set_user} via FadrixSYS:</strong> {msg}',
                                pinned=False,
                                gid=id_task
                            )

                        case "image" | "attachment":
                            ASANA.attachment(
                                path=f'V4/assets/attachment/order/{self.set_reference}',
                                file=file_name,
                                gid=id_task,
                                img=True if type_msg == "image" else False
                            )

                            ASANA.stories(
                                text=f'<strong>{self.set_user} via FadrixSYS:</strong> ANEXOU > {file_name}',
                                pinned=False,
                                gid=id_task
                            )

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_asana() == EXCEPTION INSERT ASANA: {exc}\n') ##DEBUG
            self.snackbar.warning("Não foi possível enviar o comentário para o Asana.")
            self.page.update()


    def __clear_actions(self) -> None:
        """ Normaliza (limpa) os campos de entradas do usuário. """

        try:
            self.set_note_text.current.value = None
            self.set_note_text.current.update()
            self.check_asana.current.value=False
            self.check_asana.current.update()
            self.page.update()
            self.__clear_uploads()

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __clear_actions() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def __clear_uploads(self):
        """ Limpa o diretório de uploads quando for anexado imagem ou documentos nos comentários. """

        try:
            path_dir = f'V4/upload/{self.set_reference}'
            if os.path.isdir(path_dir):
                shutil.rmtree(path=path_dir, ignore_errors=True)

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __clear_uploads() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def __move_file(self, file_name:str) -> bool:
        """ Move o arquivo do diretório de uploadas para o diretório de anexos do pedido. """

        try:
            order_attch_directory = Path(f"V4/assets/attachment/order/{self.set_reference}")
            file_attch_directory = Path(f"V4/assets/attachment/order/{self.set_reference}/{file_name}")
            order_upload_directory = Path(f'V4/upload/{self.set_reference}')
            file_upload_directory = Path(f'V4/upload/{self.set_reference}/{file_name}')        

            if order_attch_directory.exists():

                if file_attch_directory.exists():
                    self.snackbar.warning("Esse arquivo já está anexado no pedido.")
                    self.__clear_actions()
                    return False

                else:
                    shutil.move(src=file_upload_directory, dst=order_attch_directory)
                    return True

            else:
                shutil.move(src=order_upload_directory, dst="V4/assets/attachment/order")
                return True

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __move_file() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()
            self.__clear_actions()
            return False


    def __download_attachment(self, e):
        """ Adiciona opção do usuário baixar o arquivo anexado no pedido. """

        try:
            print(f'\n⬇️ NOTETEMPLATE > __download_attachment() == DOWNLOAD FILE: {e.control.data}, por {self.set_user}\n')
            self.page.launch_url(url=f'http://192.168.1.35:62024/{e.control.data}')

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __download_attachment() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()

    ## ------



    ## EVENTOS INSERIR NOTAS ------

    def __insert_text(self, e):
        """ Inseri um novo comentário de texto no sistema. """

        try:
            note_date = DATE()
            note_text = e.control.value

            if len(note_text) > 3:
                insert_DB = self.__insert_DB(note_date, "text", note_text)
            else:
                self.snackbar.warning("Não é possível inserir comentários com menos de três carecteres.")
                return None

            if not insert_DB:
                self.snackbar.internal_error()
                return None

            self.__insert_note(note_date, "text", note_text)

            self.__insert_asana(type_msg="text", msg=note_text)

            self.__clear_actions()

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_text() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.warning("Não possível inserir o comentário.")
            self.page.update()


    def __insert_image_result(self, e:ft.FilePickerResultEvent):
        """ Faz o upload do arquivo de imagem para o diretório de uploads. """

        try:
            upload_list = []
            if self.image_file.result != None and self.image_file.result.files != None:
                for f in self.image_file.result.files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            f.name,
                            upload_url=self.page.get_upload_url(f'/{self.set_reference}/{f.name}', 600),
                        )
                    )

                self.image_file.upload(upload_list)

            self.page.update()

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_image_result() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def __insert_image_progress(self, e:ft.FilePickerUploadEvent):

        try:
            if e.error == None:
                if e.progress == 1.0:

                    move_file = self.__move_file(e.file_name)
                    if not move_file:
                        self.snackbar.internal_error()
                        return None

                    note_date = DATE()
                    insert_DB = self.__insert_DB(note_date, "image", f"assets/attachment/order/{self.set_reference}/{e.file_name}")
                    if not insert_DB:
                        self.snackbar.internal_error()
                        return None

                    self.__insert_note(note_date, "image", f"assets/attachment/order/{self.set_reference}/{e.file_name}")

                    self.__insert_asana(type_msg="image", file_name=e.file_name)

                    self.__clear_actions()

            else:
                print(f'\n❌ NOTETEMPLATE > __insert_image_progress() == ERRO DE UPLOAD: {e.error}\n') ##DEBUG
                self.snackbar.warning("Houve um erro ao fazer o upload do arquivo. Tente novamente ou contate o suporte.")
                self.page.update()

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_image_progress() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.warning("Não possível fazer o upload do arquivo. Tente novamente ou contate o suporte.")
            self.page.update()        


    def __insert_attachment_result(self, e:ft.FilePickerResultEvent):
        """ Faz o upload do arquivo de aenxo para o diretório de uploads. """

        try:
            upload_list = []
            if self.attachment_file.result != None and self.attachment_file.result.files != None:
                for f in self.attachment_file.result.files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            f.name,
                            upload_url=self.page.get_upload_url(f'/{self.set_reference}/{f.name}', 600),
                        )
                    )

                self.attachment_file.upload(upload_list)

            self.page.update()

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_attachment_result() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.internal_error()
            self.page.update()


    def __insert_attachment_progress(self, e:ft.FilePickerUploadEvent):

        try:
            if e.error == None:
                if e.progress == 1.0:

                    move_file = self.__move_file(e.file_name)
                    if not move_file:
                        self.snackbar.internal_error()
                        return None

                    note_date = DATE()
                    insert_DB = self.__insert_DB(note_date, "attachment", f"assets/attachment/order/{self.set_reference}/{e.file_name}")
                    if not insert_DB:
                        self.snackbar.internal_error()
                        return None

                    self.__insert_note(note_date, "attachment", f"assets/attachment/order/{self.set_reference}/{e.file_name}")

                    self.__insert_asana(type_msg="attachment", file_name=e.file_name)

                    self.__clear_actions()

            else:
                print(f'\n❌ NOTETEMPLATE > __insert_attachment_progress() == ERRO DE UPLOAD: {e.error}\n') ##DEBUG
                self.snackbar.warning("Houve um erro ao fazer o upload do arquivo. Tente novamente ou contate o suporte.")
                self.page.update()

        except Exception as exc:
            print(f'\n❌ NOTETEMPLATE > __insert_attachment_progress() == EXCEPTION: {exc}\n') ##DEBUG
            self.snackbar.warning("Não possível fazer o upload do arquivo. Tente novamente ou contate o suporte.")
            self.page.update()

    ## ------

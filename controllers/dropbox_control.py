from source.api.dropboxApi import DropboxAPI as DBX


class DropboxControl():

    def __init__(self, category:str=None) -> None:

        self.category = category

        match category:
            case "system":
                self.path = "assets/images/system"
            case "thumbnails":
                self.path = "assets/images/thumbnails"
            case "profile":
                self.path = "assets/images/profile"
            case _:
                self.path = "upload"


    def upload(self, file_name:str):

        """ Controla o upload de arquivos para armazenamento no Dropbox """

        try:
            DBX().upload_file(
                local_path=self.path,
                local_file=file_name,
                dropbox_file_path=f"/{self.path}/{file_name}"
            )

        except Exception as exp:
            print(f'L33 - {exp}') #debug
            raise exp

    def download(self, file:dict):

        """ Controla o download de arquivos para armazenamento no Dropbox """

        try:
            DBX().download_file(
                dropbox_file_path=f'{self.path}/{file["name"]}',
                local_file_path=file["path"]
            )

        except Exception as exp:
            print(f'L48 - {exp}') #debug
            raise exp

    def delete(self, path):

        """ Controla a exclusão de arquivos no Dropbox """

        try:
            DBX().delete_file(
                path=path
            )

        except Exception as exp:
            print(f'L48 - {exp}') #debug
            raise exp

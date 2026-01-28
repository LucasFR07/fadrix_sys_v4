import os, shutil


class File():

    def __init__(self, name:str=None, size:str=None, src:str=None, dst:str=None, rename:str=None) -> None:

        self.name = name
        self.size = size
        self.path_src = src.replace("\\", "/") if src != None else None
        self.path_dst = dst.replace("\\", "/") if dst != None else None
        self.rename_file = rename


    def exist(self) -> bool:

        """ Verifica pelo caminho do arquivo (path) o mesmo existe ou não no local """

        if os.path.exists(self.path_src):
            return True
        else:
            return False

    def copy(self) -> bool:

        """ Copia um arquivo de um diretorio incial para outro especificado, preservando os metadados """

        try:
            shutil.copy2(self.path_src, self.path_dst)
            if self.rename_file != None:
                self.rename()
            return True
        except Exception as exp:
            print(exp)
            return False

    def rename(self):

        """ Renomeia um arquivo """

        try:
            name = f'{self.path_dst}/{self.name}'
            rename = f'{self.path_dst}/{self.rename_file}.png'
            os.rename(name, rename)
            return True
        except Exception as exp:
            print(exp)
            return False

    def delete(self):

        """ Delete um arquivo no caminho (path) especificado """

        if self.exist():
            os.remove(self.path_src)

from PIL import Image
import os, shutil, requests
from pathlib import Path

from controllers.file_control import File as FILE


class ImageControl():

    def __init__(self):
        self.path_download = 'download'
        self.path_thumbnails = 'assets/images/thumbnails'
        self.join_path = []


    def __walk(self, path):
        for directory, subdirectories, files in os.walk(path):
            for file in files:
                self.__resize(f'{directory}/{file}'.replace("\\", "/"))
                self.join_path.append(os.path.join(directory, file).replace("\\", "/"))
        # print(self.join_path) #DEBUG
        return self.join_path


    def __resize(self, path):
        get = Image.open(path)
        if get.height != 709:
            baseheight = 709
            hpercent = (baseheight/float(get.size[1]))
            wsize = int((float(get.size[0])*float(hpercent)))
            get_resize = get.resize((wsize,baseheight), Image.Resampling.LANCZOS)
            name = get.filename
            get_resize.save(name)


    def new_image(self, path:str):
        self.__walk(path)
        if len(self.join_path) == 0:
            return None
        width, height = [], []
        img_width, max_height, line_img, start = 0, 0, 0, 0

        length = int(len(self.join_path))
        for image in self.join_path:
            get = Image.open(image)
            width.append(int(get.width))
            height.append(int(get.height))

        match length:
            case 4 | 5 | 6 | 7 | 8 | 10 | 13 | 14 | 16 | 20:
                max_height = 2
            case 9 | 11 | 12 | 15 | 16 | 17 | 18 | 19 | 30:
                max_height = 3
            case 40:
                max_height = 4
            case 50:
                max_height = 5
            case _:
                max_height = 1

        if (length%max_height) != 0:
            match max_height:
                case 2:
                    stop = int((length +1)/2)
                case 3:
                    stop = int((length -1)/2)
        else:
            stop = int(length/max_height)

        new_image = Image.new(mode="RGB", size=(sum(width[0:stop]), (max(height)*max_height)), color="white")
        while line_img < max_height:
            for new_img in self.join_path[start:stop]:
                get = Image.open(new_img)
                new_image.paste(get, (img_width, ((max(height)+1)*line_img)))
                img_width += get.width
            img_width = 0
            line_img+=1
            start = stop
            stop+=stop

        file_name = "print.jpg"
        new_image.save(f'{path}/{file_name}') 
        return file_name


    def create_thumbnails_products(self, img:str):
        create = Image.open(f'{self.path_download}/{img}.jpg')
        create.thumbnail(size=(236,236))
        file_name = f'{img}_thumb.jpg'
        create.save(f'{self.path_thumbProducts}/{file_name}')
        return "Thumbnails criado com sucesso"


    def download(self, path, name, url):        
        try:
            # print(f"IMAGE_CONTROL > download() ==> FILE: {path} | {name} | {url}") ##DEBUG
            img_url = url
            img = Image.open(requests.get(img_url, stream = True).raw)
            img.save(f'{path}/{name}')

        except Exception as exc:
            print(f"IMAGE_CONTROL > download() ==> {exc}") ##DEBUG            
            # shutil.copy2(
            #     src="D:/FADRIX/DEVELOPER/FADRIX-SYS/V4/assets/images/system/nopreview.png",
            #     dst=path
            # )
            return None


    def clear_download(self):
        for files in os.listdir(self.path_download):
            os.remove(os.path.join(self.path_download, files))


    def clear_path(self, path:str):
        """ Exclui a pasta do pedido após o upload da imagem. """

        try:
            download_directory = Path(path)
            if download_directory.exists():
                shutil.rmtree(path=path, ignore_errors=False)

        except Exception as exc:
            print(f'\n❌ IMAGE_CONTROL > clear_path() ==> EXCEPTION: {exc}\n')
            return None

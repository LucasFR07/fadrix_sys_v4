import barcode
from barcode.writer import ImageWriter


class BarCode:

    def __init__(self, name:str, data, barcode_format, options=None) -> None:

        self.name = name
        self.data = data
        self.barcode_format = barcode_format
        self.options = options

        self.__generate_barcode()


    def __generate_barcode(self):
        # Get the barcode class corresponding to the specified format 
        barcode_class = barcode.get_barcode_class(self.barcode_format)
        # Create a barcode image using the provided data and format
        barcode_image = barcode_class(self.data, writer=ImageWriter())
        # Save the barcode image to a file named "barcode" with the specified options
        barcode_image.save(self.name, options=self.options)



# __BARCODE_MAP = {
#     "ean8": EAN8,
#     "ean8-guard": EAN8_GUARD,
#     "ean13": EAN13,
#     "ean13-guard": EAN13_GUARD,
#     "ean": EAN13,
#     "gtin": EAN14,
#     "ean14": EAN14,
#     "jan": JAN,
#     "upc": UPCA,
#     "upca": UPCA,
#     "isbn": ISBN13,
#     "isbn13": ISBN13,
#     "gs1": ISBN13,
#     "isbn10": ISBN10,
#     "issn": ISSN,
#     "code39": Code39,
#     "pzn": PZN,
#     "code128": Code128,
#     "itf": ITF,
#     "gs1_128": Gs1_128,
#     "codabar": CODABAR,
#     "nw-7": CODABAR,
# }
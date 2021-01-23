from models.nst_model import NSTModel
from models.cgan_model import CGANModel


class ImgStyle:

    def __init__(self, imsize=None):
        self.imsize = imsize

    def nst_stylize(self, content_img, style_img):
        nst_model = NSTModel(self.imsize, style_img)
        stylized_image = nst_model.get_stylized_image(content_img)

        return stylized_image

    @staticmethod
    def cgan_stylize(content_img, style: str):
        cgan_model = CGANModel(style)
        stylized_image = cgan_model.get_stylized_image(content_img)

        return stylized_image

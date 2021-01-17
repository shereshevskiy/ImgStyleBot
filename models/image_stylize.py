from models.style_transfer import NSTModel


class ImgStyle:

    def __init__(self, imsize=128):
        self.imsize = imsize

    def nst_stylize(self, content_img, style_img):
        nst_model = NSTModel(self.imsize)
        stylized_image = nst_model.get_stylized_image(content_img, style_img)

        return stylized_image

    def gan_stylize(self, content_img, style: str):
        # TODO

        return content_img

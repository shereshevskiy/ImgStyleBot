import os

import torch
from torchvision.transforms import transforms

from config import ROOT_DIR
from models.cgan_settings import output_nc, input_nc
from models.cgan_utils import Generator


class CGANModel:

    def __init__(self, style: str):
        self.style = style
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def get_stylized_image(self, content_img):
        # funcs init
        generator = self.make_generator()
        transformer = self.make_transformer()
        tensor2img = transforms.ToPILImage()  # функция для тензор в картинку

        content_img = transformer(content_img).unsqueeze(0).to(self.device, torch.float)  # готовим картинку
        output = 0.5 * (generator(content_img.to(self.device)).data + 1.0)  # преобразование
        image = tensor2img(output.squeeze(0).cpu().clone())  # преобразуем выход в картинку
        return image

    def make_generator(self):
        netG_B2A = Generator(output_nc, input_nc).to(self.device)
        netG_B2A_path = os.path.join(ROOT_DIR, 'models', 'cgan_checkpoints', self.style, 'netG_B2A.pth')
        netG_B2A.load_state_dict(torch.load(netG_B2A_path, map_location=self.device))
        netG_B2A.eval()
        return netG_B2A

    @staticmethod
    def make_transformer():
        transformer = transforms.Compose(
            [transforms.ToTensor(),
             transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))]
        )
        return transformer

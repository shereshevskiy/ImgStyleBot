"""
import io
from PIL import Image

#Получение
file_id = message.photo[-1].file_id
file_info = bot.get_file(file_id)
image_data = bot.download_file(file_info.file_path)
img = Image.open(io.BytesIO(image_data))

#отправка
img_data = #изображение PIL
bio = io.BytesIO()
bio.name = 'image.jpeg'
img_data.save(bio, 'JPEG')
bio.seek(0)
bot.send_photo(chat_id, photo=bio)

"""
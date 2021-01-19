# import urllib
import io
import os
from collections import defaultdict
import telebot
from PIL import Image
from telebot import types
from models.image_stylize import ImgStyle
from dotenv import load_dotenv
# import numpy as np

from .settings import gan_styles, start_buttons, START_TEXT, variants
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# init of store for photo ids
PHOTO_IDs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

# init stats
START, CONTENT, STYLE_NST, GAN = range(4)
USER_STATE = defaultdict(lambda: START)


# set of stat func
def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


# *************** bot ***************

def my_bot():
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=["style_start"])
    def handle_style_start(message):
        text = """
Пришлите картинку, которую Вы хотите стилизовать (картинку с контентом)
               """
        bot.send_message(message.chat.id, text=text)
        update_state(message, CONTENT)

    @bot.message_handler(func=lambda message: get_state(message) == CONTENT, content_types=['photo'])
    def handle_content(message):
        photo_id = message.photo[0].file_id
        PHOTO_IDs[message.chat.id]["content"] = photo_id

        text = """
        Ваша картинка получена :)
        Будем ее стилизовать.
        Стилизацию можно сделать двумя способами:
        
1) Стиль задаете Вы. Нужно будет прислать картинку, которая будет использована как образец стиля. Например - любая 
картина Вангога, Моне и тп. Это будет дольше, придется подождать 3-5 минут

2) Стиль выбирается из уже предустановленных здесь (Стиль на выбор). 
Это будет быстрее, около 1-2 минут

    Укажите, пожалуйста, какой вариант Вы выбираете?
        """

        def create_keyboard():
            buttons_list = variants
            keyboard_ = types.InlineKeyboardMarkup(row_width=2)
            buttons = [types.InlineKeyboardButton(text=item, callback_data=item) for item in buttons_list]
            keyboard_.add(*buttons)
            return keyboard_

        keyboard = create_keyboard()
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard)

    # обрабатываем кнопки
    @bot.callback_query_handler(func=lambda x: True)
    def content_callback_handler(callback_query):
        message = callback_query.message
        callback_text = callback_query.data

        if callback_text == variants[0]:
            text = """
            Пришлите, пожалуйста, картинку со стилем
            """
            bot.send_message(message.chat.id, text=text)
            update_state(message, STYLE_NST)

        elif callback_text == variants[1]:
            gan_styles_str = '\n'.join(gan_styles.keys())
            text = f"""
            Список стилей:
            \n{gan_styles_str}
            
            Выберите, пожалуйста, и вышлите название стиля
            (можно использовать кнопки внизу)
            """
            keyboard_styles = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard_styles.row(*gan_styles.keys())
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            update_state(message, GAN)

    @bot.message_handler(func=lambda message: get_state(message) == STYLE_NST, content_types=["photo"])
    def handle_style_NST(message):
        if message.photo:
            # обрабатываем входящее сообщение
            photo_id = message.photo[0].file_id
            PHOTO_IDs[message.chat.id]["style"] = photo_id

            # готовим NST-стилизацию
            content_id = PHOTO_IDs[message.chat.id]["content"]
            content_info = bot.get_file(content_id)
            content_img = bot.download_file(content_info.file_path)
            content_img = Image.open(io.BytesIO(content_img))

            style_id = PHOTO_IDs[message.chat.id]["style"]
            style_info = bot.get_file(style_id)
            style_img = bot.download_file(style_info.file_path)
            style_img = Image.open(io.BytesIO(style_img))

            # делаем стилизацию и высылаем в чат
            bot.send_message(message.chat.id, text="Ожидайте 3-5 минуты...")
            img_style = ImgStyle()
            stylized_img = img_style.nst_stylize(content_img, style_img)
            bot.send_photo(message.chat.id, stylized_img)
            update_state(message, START)
        else:
            text = f"""
                    Картинку со стилем не получил. 
                    Жду картинку со стилем, высылайте )
                    """
            bot.send_message(message.chat.id, text=text)

    @bot.message_handler(func=lambda message: get_state(message) == GAN)
    def handle_GAN(message):
        style_key = message.text
        if style_key not in gan_styles.keys():
            text = f"Хм...этот стиль мне неизвестен... Введите один из номеров {', '.join(gan_styles.keys())}"
            bot.send_message(message.chat.id, text=text)
        else:
            content_id = PHOTO_IDs[message.chat.id]["content"]
            file_info = bot.get_file(content_id)
            content_img = bot.download_file(file_info.file_path)
            # делаем стилизацию и высылаем в чат
            bot.send_message(message.chat.id, text="Ожидайте 1-2 минут...")
            img_style = ImgStyle()
            stylized_img = img_style.gan_stylize(content_img, gan_styles[style_key])
            bot.send_photo(message.chat.id, stylized_img)
            update_state(message, START)

    @bot.message_handler(commands=["gan_styles"])
    def handle_styles(message):
        gan_styles_str = '\n'.join(gan_styles.keys())
        text = f"""
        Список предустановленных стилей
        \n{gan_styles_str}
        """
        bot.send_message(message.chat.id, text=text)

    @bot.message_handler(commands=["help"])
    def handle_help(message):
        text = """
/start - начало общения с ботом

/style_start - старт стилизации

/help - помощь

/gan_styles - список предустановленных стилей
        """
        bot.send_message(message.chat.id, text=text)

    @bot.message_handler(commands=["start"])
    def handle_start(message):
        keyboard_start = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_start.row(*start_buttons)
        bot.send_message(message.chat.id, text=START_TEXT, reply_markup=keyboard_start)
        update_state(message, START)

    @bot.message_handler()
    def handle_any(message):
        keyboard_start = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_start.row(*start_buttons)
        bot.send_message(message.chat.id, text=START_TEXT, reply_markup=keyboard_start)
        update_state(message, START)

    bot.polling()


if __name__ == '__main__':
    my_bot()

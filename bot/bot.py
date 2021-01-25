# import urllib
import io
import os
from collections import defaultdict
import telebot
from PIL import Image
from telebot import types

from models.image_stylize import ImgStylize
from dotenv import load_dotenv
# import numpy as np
from config import nst_imsize
from bot.bot_settings import gan_styles, start_buttons, START_TEXT, variants, main_menu, commands_descr, commands

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# init of store for photo ids
PHOTO_IDs = defaultdict(lambda: defaultdict(lambda: None))

# init stats
START, START_CONTENT, CONTENT, NST, STYLE, GAN = range(6)
USER_STATE = defaultdict(lambda: START)


# set of stat func
def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


# *************** bot ***************

def my_bot():
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=[commands["start"]])
    def handle_start(message):
        text = """
Пришлите картинку, которую Вы хотите стилизовать (картинку с контентом)
               """
        bot.send_message(message.chat.id, text=text)
        update_state(message, START_CONTENT)

    @bot.message_handler(commands=[commands["help"]])
    def handle_help(message):
        all_commands_str = "\n\n".join([f"/{k} - {v}" for k, v in commands_descr.items()])
        text = f"""
        Список всех команд

{all_commands_str}
        """
        keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(func=lambda message: get_state(message) == START_CONTENT, content_types=['photo'])
    def handle_content(message):
        photo_id = message.photo[0].file_id
        PHOTO_IDs[message.chat.id][commands["content_img"]] = photo_id

        text = f"""
        Ваша картинка получена :)
        Будем ее стилизовать.
        Стилизацию можно сделать двумя способами:
        
1) Медленный вариант. Здесь стиль задаете Вы. Нужно прислать картинку, которая будет использована как образец стиля. 
Например - любая картина в стиле барокко, абстракционизм и тп. Кнопка {commands["nst"]} Придется подождать 3-5 минут 

2) Быстрый вариант. Тут стиль выбирается из уже предустановленных
Кнопка {commands["gan"]} 
Займет около полу минуты

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
    def variants_callback_handler(callback_query):
        message = callback_query.message
        callback_text = callback_query.data

        if callback_text == variants[0]:
            text = """
            Пришлите, пожалуйста, картинку со стилем
            """
            bot.send_message(message.chat.id, text=text)
            update_state(message, NST)

        elif callback_text == variants[1]:
            fast_styles_str = '\n'.join(gan_styles.keys())
            text = f"""
            Список стилей:
            \n{fast_styles_str}
            
            Выберите, пожалуйста, и вышлите название стиля
            (можно использовать кнопки внизу)
            """
            keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
            keyboard_styles.row(*gan_styles.keys())
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            update_state(message, GAN)

    @bot.message_handler(func=lambda message: get_state(message) == NST, content_types=["photo"])
    @bot.message_handler(commands=[commands["nst"]])
    def handle_nst_NST(message):
        if message.photo:
            # обрабатываем входящее сообщение
            photo_id = message.photo[0].file_id
            PHOTO_IDs[message.chat.id][commands["style_img"]] = photo_id

        content_id = PHOTO_IDs[message.chat.id][commands["content_img"]]
        if content_id is None:
            text = f"""
Нет картинки контента.
Можете ввести ее прямо сейчас
"""
            update_state(message, CONTENT)

            keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
            keyboard_styles.row("/" + commands["content_img"])
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            return

        style_id = PHOTO_IDs[message.chat.id][commands["style_img"]]
        if style_id is None:
            text = f"""
Нет картинки стиля.
Можете ввести ее прямо сейчас
"""
            update_state(message, STYLE)

            keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
            keyboard_styles.row("/" + commands["style_img"])
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            return

        # готовим NST-стилизацию
        content_info = bot.get_file(content_id)
        content_img = bot.download_file(content_info.file_path)
        content_img = Image.open(io.BytesIO(content_img))  # to PIL Image format

        style_info = bot.get_file(style_id)
        style_img = bot.download_file(style_info.file_path)
        style_img = Image.open(io.BytesIO(style_img))  # to PIL Image format

        # делаем стилизацию и высылаем в чат
        bot.send_message(message.chat.id, text="Ожидайте 3-5 минут...")
        img_stylizer = ImgStylize(nst_imsize)
        stylized_img = img_stylizer.nst_stylize(content_img, style_img)
        bot.send_photo(message.chat.id, stylized_img)
        del img_stylizer

        # готовим для следующуй стилизации
        text = f"""
Что дальше? 
Можете сменить входные картинки или выбрать вариант стилизации.
Используйте кнопки внизу или /{commands["help"]}
"""
        keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(commands=[commands["style_img"]])
    def handle_style(message):
        text = f"""
Пришлите картинку стиля
/{commands["help"]} 
"""
        update_state(message, STYLE)

        keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(func=lambda message: get_state(message) == STYLE, content_types=["photo"])
    def handle_style_photo(message):
        if message.photo:
            # обрабатываем входящее сообщение
            photo_id = message.photo[0].file_id
            PHOTO_IDs[message.chat.id][commands["style_img"]] = photo_id

        # готовим для следующую стилизации
        text = f"""
Картинка-стиль есть )
Далее /{commands["nst"]}, кнопки внизу или любая команда
/{commands["help"]}
"""
        keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(commands=[commands["content_img"]])
    def handle_content(message):
        text = f"""
Пришлите картинку контента (стилизуемую) 
/{commands["help"]}
"""
        keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        update_state(message, CONTENT)

    @bot.message_handler(func=lambda message: get_state(message) == CONTENT, content_types=["photo"])
    def handle_content_photo(message):
        if message.photo:
            # обрабатываем входящее сообщение
            photo_id = message.photo[0].file_id
            PHOTO_IDs[message.chat.id][commands["content_img"]] = photo_id

        # готовим для следующую стилизации
        text = f"""
Картинка-контент есть ) 
Далее /{commands["nst"]}, /{commands["gan"]} или кнопки внизу
/{commands["help"]}
"""
        keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(commands=[commands["gan"]])
    def handle_gan(message):
        fast_styles_str = '\n'.join(gan_styles.keys())
        text = f"""
Список стилей:
\n{fast_styles_str}

Выберите, пожалуйста, и вышлите название стиля
(можно использовать кнопки внизу)
"""
        keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*gan_styles.keys())
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        update_state(message, GAN)

    @bot.message_handler(func=lambda message: (get_state(message) == GAN) & (message.text in gan_styles.keys()))
    def handle_GAN(message):
        fast_style = message.text
        if fast_style in gan_styles.keys():
            PHOTO_IDs[message.chat.id]["fast_style"] = fast_style

            content_id = PHOTO_IDs[message.chat.id][commands["content_img"]]
            if content_id is None:
                text = f"""
Нет картинки контента.
Можете ввести ее прямо сейчас
"""
                update_state(message, CONTENT)

                keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
                keyboard_styles.row("/" + commands["content_img"])
                bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
                return

            file_info = bot.get_file(content_id)
            content_img = bot.download_file(file_info.file_path)
            content_img = Image.open(io.BytesIO(content_img))  # to PIL Image format
            # делаем стилизацию и высылаем в чат
            bot.send_message(message.chat.id, text="Ожидайте около пол минуты...")
            img_stylizer = ImgStylize()
            stylized_img = img_stylizer.cgan_stylize(content_img, gan_styles[fast_style])
            bot.send_photo(message.chat.id, stylized_img)
            del img_stylizer

            text = f"Еще раз?\nИли /{commands['help']} для других команд"
            keyboard_styles = telebot.types.ReplyKeyboardMarkup(True)
            keyboard_styles.row(*gan_styles.keys())
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        else:
            text = f"Хм...этот стиль мне неизвестен... Введите один из следующих стилей {', '.join(gan_styles.keys())}"
            bot.send_message(message.chat.id, text=text)

    @bot.message_handler(commands=[commands["gan_styles"]])
    def handle_styles(message):
        fast_styles_str = '\n'.join(gan_styles.keys())
        text = f"""
        Список предустановленных стилей
        \n{fast_styles_str}
        """
        bot.send_message(message.chat.id, text=text)

    @bot.message_handler()
    def handle_any(message):
        keyboard_start = telebot.types.ReplyKeyboardMarkup(True)
        keyboard_start.row(*start_buttons)
        bot.send_message(message.chat.id, text=START_TEXT, reply_markup=keyboard_start)
        update_state(message, START)

    bot.polling()


if __name__ == '__main__':
    my_bot()

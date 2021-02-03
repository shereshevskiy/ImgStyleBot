import io
import os
from collections import defaultdict
import telebot
from PIL import Image
from telebot import types

from models.image_stylize import ImgStylize
from dotenv import load_dotenv
from config import nst_imsize
from bot.bot_settings import (gan_styles, nst_styles, start_menu, START_TEXT, variants, main_menu,
                              commands, commands_aliases, style_imp_path)
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
nst_styles_str = "\n".join([f"{num+1} {style_name}" for num, style_name in enumerate(nst_styles.keys())])
gan_styles_str = '\n'.join(gan_styles.keys())

# init of store for photo ids
PHOTO_IDs = defaultdict(lambda: defaultdict(lambda: None))

# init of stats
START, START_CONTENT, CONTENT, NST, GAN = range(5)
USER_STATE = defaultdict(lambda: START)


# set of stat func
def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


# *************** bot ***************
def my_bot():
    bot = telebot.TeleBot(TOKEN)

    # set commands
    set_commands = [types.BotCommand(f"/{command}", description) for command, description in commands.items()]
    bot.set_my_commands(set_commands)

    @bot.message_handler(commands=[commands_aliases["run"]])
    def handle_run(message):
        text = """
Пришлите картинку, которую Вы хотите изменить (стилизовать)
"""
        bot.send_message(message.chat.id, text=text)
        update_state(message, START_CONTENT)

    @bot.message_handler(commands=[commands_aliases["help"]])
    def handle_help(message):
        all_commands_str = "\n\n".join([f"/{k} - {v}" for k, v in commands.items()])
        text = f"""
        Список всех команд

{all_commands_str}
        """
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        update_state(message, START)

    @bot.message_handler(commands=[commands_aliases["start"], commands_aliases["hello"]])
    def handle_start(message):
        keyboard_start = types.ReplyKeyboardMarkup(True)
        keyboard_start.row(*start_menu)
        bot.send_message(message.chat.id, text=START_TEXT, reply_markup=keyboard_start)
        update_state(message, START)

    @bot.message_handler(func=lambda message: get_state(message) == START_CONTENT, content_types=['photo'])
    def handle_START_CONTENT(message):
        photo_id = message.photo[0].file_id
        PHOTO_IDs[message.chat.id]["content_img"] = photo_id

        text = f"""
Ваша картинка получена :)
Будем ее стилизовать.
Стилизацию можно сделать двумя способами:
        
1) Медленный вариант. Здесь стиль ЗАДАЕТЕ ВЫ. Нужно прислать картинку, которая будет использована как образец стиля. 
Например - любая картина в стиле барокко, абстракционизм и тп. Кнопка {commands_aliases["nst"]} 
Придется подождать 3-5 минут. 
А ещё тут можно использовать и уже ПРЕДУСТАНОВЛЕННЫЕ стили 

2) Быстрый вариант. Тут стиль выбирается из уже ПРЕДУСТАНОВЛЕННЫХ
Кнопка {commands_aliases["gan"]} 
Займет около пол минуты

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
            text = f"""
            Пришлите картинку стиля
            или
            выберите стиль из имеющихся:

            {nst_styles_str}

            Пришлите картинку или номер стиля
            /{commands_aliases["help"]} 
            """
            keyboard_styles = types.ReplyKeyboardMarkup(True)
            keyboard_styles.row(*main_menu)
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

            update_state(message, NST)

        elif callback_text == variants[1]:
            text = f"""
            Список стилей:
            \n{gan_styles_str}
            
            Выберите, пожалуйста, и вышлите название стиля
            (можно использовать кнопки внизу)
            """
            keyboard_styles = types.ReplyKeyboardMarkup(True)
            keyboard_styles.row(*gan_styles.keys())
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            update_state(message, GAN)

    @bot.message_handler(commands=[commands_aliases["nst"]])
    def handle_nst(message):
        # if message.photo:
        #     # обрабатываем входящее сообщение
        #     photo_id = message.photo[0].file_id
        #     PHOTO_IDs[message.chat.id][commands_aliases["style_img"]] = photo_id

        content_id = PHOTO_IDs[message.chat.id]["content_img"]
        if content_id is None:
            text = f"""
Нет изменяемой (стилизуемой) картинки.
Можете ввести ее прямо сейчас
"""
            keyboard_styles = types.ReplyKeyboardMarkup(True)
            keyboard_styles.row(*main_menu)
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            update_state(message, CONTENT)
            return

        style_id = PHOTO_IDs[message.chat.id][commands_aliases["style_img"]]
        nst_style_filename = PHOTO_IDs[message.chat.id]["nst_style_filename"]
        if (style_id is None) and (nst_style_filename is None):
            text = f"""
Нет картинки стиля.
Пришлите картинку стиля или выберите из имеющихся:

{nst_styles_str}

Можете прислать картинку или номер стиля прямо сейчас:
"""
            keyboard_styles = types.ReplyKeyboardMarkup(True)
            keyboard_styles.row(*main_menu)
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            update_state(message, NST)
            return

        # готовим nst-стилизацию
        content_info = bot.get_file(content_id)
        content_img = bot.download_file(content_info.file_path)
        content_img = Image.open(io.BytesIO(content_img))  # to PIL Image format

        if style_id:
            style_info = bot.get_file(style_id)
            style_img = bot.download_file(style_info.file_path)
            style_img = Image.open(io.BytesIO(style_img))  # to PIL Image format
            nst_style_name = "-"
            
        else:
            nst_style_filename = nst_style_filename or "NaN"
            style_img = Image.open(os.path.join(style_imp_path, nst_style_filename))
            nst_style_name = PHOTO_IDs[message.chat.id]["nst_style_name"]

        # делаем стилизацию и высылаем в чат
        text = """
Ожидайте. Обычно 3-5 минут, иногда до 10-15 ...      
"""
        bot.send_message(message.chat.id, text=text)
        img_stylizer = ImgStylize(nst_imsize)
        stylized_img = img_stylizer.nst_stylize(content_img, style_img)
        bot.send_photo(message.chat.id, stylized_img, f"Стиль: {nst_style_name}")
        del img_stylizer

        # готовим для следующей стилизации
        text = f"""
Ваш результат :) 
Далее можете повторить: сменить входные картинки или выбрать вариант стилизации.
Используйте кнопки внизу или /{commands_aliases["help"]}
"""
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(commands=[commands_aliases["style_img"]])
    def handle_style_img(message):
        text = f"""
Пришлите картинку стиля
или
выберите стиль из имеющихся:

{nst_styles_str}

Пришлите картинку или номер стиля
/{commands_aliases["help"]} 
"""
        update_state(message, NST)

        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(commands=[commands_aliases["content_img"]])
    def handle_content_img(message):
        text = f"""
Пришлите изменяемую картинку (стилизуемую)
/{commands_aliases["help"]}
"""
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        update_state(message, CONTENT)

    @bot.message_handler(func=lambda message: get_state(message) == CONTENT, content_types=["photo"])
    def handle_CONTENT_photo(message):
        if message.photo:
            # обрабатываем входящее сообщение
            photo_id = message.photo[0].file_id
            PHOTO_IDs[message.chat.id]["content_img"] = photo_id

        # готовим для следующую стилизации
        text = f"""
Изменяемая картинка есть ) 
Далее /{commands_aliases["nst"]}, /{commands_aliases["gan"]} или кнопки внизу
/{commands_aliases["help"]}
"""
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

    @bot.message_handler(commands=[commands_aliases["gan"]])
    def handle_gan(message):
        text = f"""
Список стилей:
\n{gan_styles_str}

Выберите, пожалуйста, и вышлите название стиля
(можно использовать кнопки внизу)
"""
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*gan_styles.keys())
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        update_state(message, GAN)

    @bot.message_handler(func=lambda message: (get_state(message) == GAN) & (message.text in gan_styles.keys()))
    def handle_GAN(message):
        gan_style = message.text
        if gan_style in gan_styles.keys():
            PHOTO_IDs[message.chat.id]["gan_style"] = gan_style

            content_id = PHOTO_IDs[message.chat.id]["content_img"]
            if content_id is None:
                text = f"""
Нет изменяемой (стилизуемой) картинки.
Можете ввести ее прямо сейчас
"""
                update_state(message, CONTENT)

                keyboard_styles = types.ReplyKeyboardMarkup(True)
                keyboard_styles.row(*main_menu)
                bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
                return

            file_info = bot.get_file(content_id)
            content_img = bot.download_file(file_info.file_path)
            content_img = Image.open(io.BytesIO(content_img))  # to PIL Image format
            # делаем стилизацию и высылаем в чат
            bot.send_message(message.chat.id, text="Ожидайте около пол минуты...")
            img_stylizer = ImgStylize()
            stylized_img = img_stylizer.cgan_stylize(content_img, gan_styles[gan_style])
            bot.send_photo(message.chat.id, stylized_img, f"Стиль: {gan_style}")
            del img_stylizer

            text = f"""
Еще раз с другим быстрым стилем?
(смотрите кнопки внизу)
/{commands_aliases['help']}
"""
            keyboard_styles = types.ReplyKeyboardMarkup(True)
            keyboard_styles.row(*gan_styles.keys())
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        else:
            text = f"Хм...этот стиль мне неизвестен... Введите один из следующих стилей {', '.join(gan_styles.keys())}"
            bot.send_message(message.chat.id, text=text)

    @bot.message_handler(commands=[commands_aliases["gan_styles"]])
    def handle_gan_styles(message):
        text = f"""
Список предустановленных БЫСТРЫХ стилей

{gan_styles_str}

Можно задать стиль, укажите название:
(можно использовать кнопки внизу)
/{commands_aliases["help"]}
"""
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*gan_styles.keys())
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        update_state(message, GAN)

    @bot.message_handler(commands=[commands_aliases["nst_styles"]])
    def handle_nst_styles(message):
        text = f"""
Список предустановленных МЕДЛЕННЫХ стилей

{nst_styles_str}

Можно задать стиль, пришлите номер:
/{commands_aliases["help"]}
"""
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
        update_state(message, NST)

    @bot.message_handler(func=lambda message: get_state(message) == NST, content_types=["photo", "text"])
    def handle_NST(message):
        PHOTO_IDs[message.chat.id][commands_aliases["style_img"]] = None
        PHOTO_IDs[message.chat.id]["nst_style_filename"] = None
        if message.photo:
            # обрабатываем входящее сообщение
            photo_id = message.photo[0].file_id
            PHOTO_IDs[message.chat.id][commands_aliases["style_img"]] = photo_id
        if message.text:
            if message.text in [str(num) for num in range(1, len(nst_styles) + 1)]:
                nst_style_name = list(nst_styles.keys())[int(message.text) - 1]
                nst_style_filename = list(nst_styles.values())[int(message.text) - 1]
                PHOTO_IDs[message.chat.id]["nst_style_filename"] = nst_style_filename
                PHOTO_IDs[message.chat.id]["nst_style_name"] = nst_style_name
                nst_style_filename = PHOTO_IDs[message.chat.id]["nst_style_filename"] or "NaN"
                style_img = Image.open(
                    os.path.join(style_imp_path, nst_style_filename)
                )
                bot.send_photo(message.chat.id, style_img, f"Образец стиля - {nst_style_name}")
            else:
                text = "Номер стиля не верный. Попробуйте ввести номер стиля еще раз или пришлите картинку стиля"
                bot.send_message(message.chat.id, text)
                # update_state(message, START)
                return

        # готовим для следующую стилизации
        text = f"""
Картинка-стиль есть )
Далее /{commands_aliases["nst"]}, кнопки внизу или любая команда
/{commands_aliases["help"]}
"""
        keyboard_styles = types.ReplyKeyboardMarkup(True)
        keyboard_styles.row(*main_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)

        update_state(message, START)

    @bot.message_handler(commands=[commands_aliases["about"]])
    def handle_about_author(message):
        text = """
Автор Дмитрий Шерешевский (c)
Подробнее об авторе здесь https://www.linkedin.com/in/dmitry-shereshevskiy/
О проекте здесь https://github.com/shereshevskiy/ImgStyleBot/blob/master/README.md
"""
        keyboard_start = types.ReplyKeyboardMarkup(True)
        keyboard_start.row(*start_menu)
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard_start)

    @bot.message_handler()
    def handle_any(message):
        keyboard_start = types.ReplyKeyboardMarkup(True)
        keyboard_start.row(*start_menu)
        bot.send_message(message.chat.id, text=START_TEXT, reply_markup=keyboard_start)
        update_state(message, START)

    bot.polling()


if __name__ == '__main__':
    my_bot()

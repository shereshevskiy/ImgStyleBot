# import urllib
from collections import defaultdict
import telebot
from telebot import types
from models.image_stylize import ImgStyle

from config import TOKEN  # , ROOT_DIR

# initialization
START_TEXT = """
    Привет! 
    Я Бот, который может стилизовать Ваши картинки. 
Я это делаю в двух вариантах: 
    - с вашим образцом стиля и 
    - с использованием предустановленных у меня стилей. 
    
    Воспользуйтесь командами: 
/stylize - для старта стилизации

/styles - список предустановленных стилей
    
/help - чтобы узнать все доступные команды
"""

# styles
styles = {
    '1': 'Monet',
    '2': 'Cezanne',
    '3': 'Ukiyoe',
    '4': 'Vangogh'
}
styles_str = '\n' + ''.join([f"\t{key}  {styles[key]}\n" for key in styles])

PHOTO_IDs = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

# state init and state func
START, CONTENT, STYLE_and_NST, GAN = range(4)
USER_STATE = defaultdict(lambda: START)


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


# initialization for keyboard
variant1 = "1) Ваш стиль"
variant2 = "2) Стиль на выбор"
buttons_list = [variant1, variant2]


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=item, callback_data=item) for item in buttons_list]
    keyboard.add(*buttons)
    return keyboard


# *************** bot ***************
def my_bot():
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=["stylize"])
    def handle_stylize(message):
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
картина Вангога, Моне и тп. Это будет дольше, придется подождать 10-15 минут 

2) Стиль выбирается из уже предустановленных здесь (Стиль на выбор). 
Это будет быстрее, около 3-5 минут

    Укажите, пожалуйста, какой вариант Вы выбираете?
        """
        keyboard = create_keyboard()
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard)

    # обрабатываем кнопки
    @bot.callback_query_handler(func=lambda x: True)
    def callback_handler(callback_query):
        message = callback_query.message
        callback_text = callback_query.data

        if callback_text == variant1:
            text = """
            Пришлите, пожалуйста, картинку со стилем
            """
            bot.send_message(message.chat.id, text=text)
            update_state(message, STYLE_and_NST)

        elif callback_text == variant2:
            text = f"""
            Список стилей:
            {styles_str}
            Выберите, пожалуйста, и вышлите номер стиля
            (можно использовать кнопки под строкой ввода)
            """
            keyboard_styles = telebot.types.ReplyKeyboardMarkup(True, True)
            keyboard_styles.row(*styles.keys())
            bot.send_message(message.chat.id, text=text, reply_markup=keyboard_styles)
            update_state(message, GAN)

    @bot.message_handler(func=lambda message: get_state(message) == STYLE_and_NST, content_types=["photo"])
    def handle_style(message):
        if message.photo:
            # обрабатываем входящее сообщение
            photo_id = message.photo[0].file_id
            PHOTO_IDs[message.chat.id]["style"] = photo_id

            # готовим NST-стилизацию
            content_id = PHOTO_IDs[message.chat.id]["content"]
            content_info = bot.get_file(content_id)
            content_img = bot.download_file(content_info.file_path)

            style_id = PHOTO_IDs[message.chat.id]["style"]
            style_info = bot.get_file(style_id)
            style_img = bot.download_file(style_info.file_path)

            # делаем стилизацию и высылаем в чат
            bot.send_message(message.chat.id, text="Ожидайте 10-15 минут...")
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
        if style_key not in styles.keys():
            text = f"Хм...этот стиль мне неизвестен... Введите один из номеров {', '.join(styles.keys())}"
            bot.send_message(message.chat.id, text=text)
        else:
            content_id = PHOTO_IDs[message.chat.id]["content"]
            file_info = bot.get_file(content_id)
            content_img = bot.download_file(file_info.file_path)
            # делаем стилизацию и высылаем в чат
            bot.send_message(message.chat.id, text="Ожидайте 3-5 минут...")
            img_style = ImgStyle()
            stylized_img = img_style.gan_stylize(content_img, styles[style_key])
            bot.send_photo(message.chat.id, stylized_img)
            update_state(message, START)

    @bot.message_handler(commands=["styles"])
    def handle_styles(message):
        text = f"""
        Список предустановленных стилей
        {styles_str}
        """
        bot.send_message(message.chat.id, text=text)

    @bot.message_handler(commands=["help"])
    def handle_help(message):
        text = """
/start - начало общения с ботом

/stylize - старт стилизации

/help - помощь

/styles - список предустановленных стилей
        """
        bot.send_message(message.chat.id, text=text)

    @bot.message_handler(commands=["start"])
    def handle_start(message):
        bot.send_message(message.chat.id, text=START_TEXT)

    @bot.message_handler()
    def handle_any(message):
        bot.send_message(message.chat.id, text=START_TEXT)

    bot.polling()


if __name__ == '__main__':
    my_bot()

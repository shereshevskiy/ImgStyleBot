import os

commands = {
    "start": "start",
    "help": "help",
    "hello": "hello",
    "nst_styles": "slow_styles",
    "gan_styles": "fast_styles",
    "nst": "slow",
    "gan": "fast",
    "style_img": "style_img",
    "content_img": "cont_img"
}

start_buttons = ["/" + commands["start"], "/" + commands["help"], "/" + commands["nst"], "/" + commands["gan"]]

commands_descr = {
    commands["start"]: "старт стилизации с подсказками",
    commands["help"]: "список всех доступных команд",
    commands["hello"]: "приветственное вводное сообщение, можно просто написать Привет",
    commands["nst_styles"]: "список предустановленных стилей для МЕДЛЕННОЙ стилизации (slow)",
    commands["gan_styles"]: "список предустановленных стилей для БЫСТРОЙ стилизации (fast)",
    commands["nst"]: "медленная стилизация (NST-алгоритм)",
    commands["gan"]: "быстрая стилизация (GAN-алгоритм)",
    commands["style_img"]: "загрузить картинку стиля для медленной стилизации",
    commands["content_img"]: "загрузить стилизуемую картинку (контент-картинку)"
}

# gan_styles
gan_styles = {
    'Моне': 'monet',
    'Сезанн': 'cezanne',
    'Укиё-э': 'ukiyoe',
    'Вангог': 'vangogh'
}

nst_styles = {
    "Андеграунд": "andegraund.jpg",
    "Авангардизм": "Avangardizm.jpg",
    "Дадаизм": "Dadaizm.jpg",
    "Декоративная живопись": "Dekorativnay.jpg",
    "Геометрический абстракционизм": "geometr.jpg",
    "Импрессионизм": "impres.jpg",
    "Клуазонизм": "kluazonizm.jpg",
    "Конструктивизм": "konstruktivizm.jpg",
    "Кубизм": "kubizm.jpg",
    "Кубофутуризм": "kubizm.jpg",
    "Лучизм": "lu4izm.jpg",
    "Метареализм": "metar.jpg",
    "Модерн": "modern.jpg",
    "Наивное искусство": "naivnoe.jpg",
    "Неоэкспрессионизм": "neoexpressionism.jpg",
    "Неопластицизм": "neopla.jpg",
    "Оп-Арт": "op-art.jpg",
    "Орфизм": "orfizm.jpg",
    "Пикассо": "picasso.jpg"
}

style_imp_path = os.path.join("models", "style_images")

# variants init
variants = [commands["nst"], commands["gan"]]

main_menu = ["/" + commands["style_img"], "/" + commands["content_img"], "/" + commands["nst"], "/" + commands["gan"]]

START_TEXT = f"""
    Привет! 
    Я Бот, который может стилизовать Ваши картинки. 
Я это делаю в двух вариантах: 
    - медленно, с вашим образцом стиля (команда /{commands["nst"]} и 
    - быстро и с использованием предустановленных у меня стилей (команда /{commands["gan"]}). 

Вы можете начать стилизацию с подсказками или отдельно ввести картинки и запустить любой вариант стилизации.

    Воспользуйтесь командами: 

/{commands["start"]} - {commands_descr[commands["start"]]}

/{commands["gan_styles"]} - {commands_descr[commands["gan_styles"]]}

/{commands["help"]} - {commands_descr[commands["help"]]}

или используйте кнопки внизу
"""

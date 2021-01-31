import os

commands_aliases = {
    "start": "start",
    "help": "help",
    "run": "run",
    "hello": "hello",
    "nst_styles": "slow_styles",
    "gan_styles": "fast_styles",
    "nst": "run_slow",
    "gan": "run_fast",
    "style_img": "set_style",
    "content_img": "set_img",
    "about_author": "about_author"
}

start_menu = ["/" + commands_aliases["run"], "/" + commands_aliases["help"], "/" + commands_aliases["nst"],
              "/" + commands_aliases["gan"]]

commands = {
    commands_aliases["start"]: "начало общения с ботом",
    commands_aliases["help"]: "список всех доступных команд",
    commands_aliases["run"]: "старт стилизации с подсказками",
    commands_aliases["hello"]: "приветственное вводное сообщение, можно просто написать Привет",
    commands_aliases["nst_styles"]: "список предустановленных стилей для МЕДЛЕННОЙ стилизации (slow)",
    commands_aliases["gan_styles"]: "список предустановленных стилей для БЫСТРОЙ стилизации (fast)",
    commands_aliases["nst"]: "медленная стилизация (NST-алгоритм)",
    commands_aliases["gan"]: "быстрая стилизация (GAN-алгоритм)",
    commands_aliases["style_img"]: "загрузить картинку стиля для медленной стилизации",
    commands_aliases["content_img"]: "загрузить стилизуемую картинку (контент-картинку)",
    commands_aliases["about_author"]: "об авторе"
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
variants = [commands_aliases["nst"], commands_aliases["gan"]]

main_menu = ["/" + commands_aliases["style_img"], "/" + commands_aliases["content_img"],
             "/" + commands_aliases["nst"], "/" + commands_aliases["gan"]]

START_TEXT = f"""
    Привет! 
    Я Бот, который может стилизовать Ваши картинки. 
Я это делаю в двух вариантах: 

    1) медленно, с вашим образцом стиля или с предустановленными образцами стилей (команда /{commands_aliases["nst"]}) 
и 
    2) быстро, с использованием предустановленных у меня стилей (команда /{commands_aliases["gan"]}). 

Вы можете начать стилизацию с подсказками или отдельно ввести картинки и запустить любой вариант стилизации.

    Воспользуйтесь командами: 

/{commands_aliases["run"]} - {commands[commands_aliases["run"]]}

/{commands_aliases["gan_styles"]} - {commands[commands_aliases["gan_styles"]]}

/{commands_aliases["nst_styles"]} - {commands[commands_aliases["nst_styles"]]}

/{commands_aliases["help"]} - {commands[commands_aliases["help"]]}

или используйте кнопки внизу
"""

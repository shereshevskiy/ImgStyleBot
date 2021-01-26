commands = {
    "start": "start",
    "help": "help",
    "hello": "hello",
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
    commands["hello"]: "приветственное вводное сообщение, можно просто Привет",
    commands["gan_styles"]: "список предустановленных стилей для быстой стилизации (fast)",
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

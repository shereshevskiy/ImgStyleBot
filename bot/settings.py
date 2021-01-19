
# initialization
START_TEXT = """
    Привет! 
    Я Бот, который может стилизовать Ваши картинки. 
Я это делаю в двух вариантах: 
    - с вашим образцом стиля и 
    - с использованием предустановленных у меня стилей. 

    Воспользуйтесь командами: 
/style_start - для старта стилизации

/gan_styles - список предустановленных стилей

/help - чтобы узнать все доступные команды

или используйте кнопки внизу
"""

start_buttons = ["/style_start", "/gan_styles", "/help"]

# gan_styles
gan_styles = {
    'Моне': 'Monet',
    'Сезанн': 'Cezanne',
    'Укиё-э': 'Ukiyoe',
    'Вангог': 'Vangogh'
}

# variants init
variants = ["Ваш стиль", "Стиль на выбор"]

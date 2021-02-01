# <center>PET-PROJECT
# <center>Стилизация изображений в телеграм-боте

## Имя телеграм-бота: *@ImgStyleBot*
### Ссылка на бота: https://t.me/ImgStyleBot
### Гитхаб репозиторий проекта: https://github.com/shereshevskiy/ImgStyleBot
### Автор: Дмитрий Шерешевский, [LinkedIn](https://www.linkedin.com/in/dmitry-shereshevskiy/)
## <center>Описание проекта
### Общая информация
1. Телеграм бот стилизует картинки, которые ему для этого передаются, в соответствие с образцом стиля. 
   Образец стиля можно передать свой или использовать предустановленные алгоритмы или образцы стилей

### Алгоритмы
2. Алгоритмы стилизации реализованы на базе **нейронных сетей**
3. Стилизация делается **двумя** способами:   
    **а)** медленный способ, реализованный на базе нейросетевого алгоритма **Style Transfer (NST)**.
   Для этого боту нужно отправить две картинки — стилизуемую картинку 
   (контент) и картинку с образцом стиля    
   - для стилизации посредством **Style Transfer** алгоритма можно также использовать **предустановленные образцы стилей**, 
     которые добавлены в качестве реализации **дополнительной функциональности**      
     
    **б)** быстрый способ, реализованный на базе нейросетевого алгоритма **CycleGAN**

4. Для алгоритма **Style Transfer** в качестве **базовой сети** использована предобученная сеть архитектуры **VGG19** 
   из библиотеки **torchvision**. Полная версия этой сети занимает около **550 мб**. Непосредственно в алгоритме 
   задействовано только первые **18** слоев этой сетки (всего их **37**). 
   Поэтому для оптимизации использования памяти, что особенно актуально для бесплатного тарифа Heroku, 
   были удалены неиспользуемые глубокие слои. В результате потребовалось всего около **9 мб** памяти

### Деплой и фреймворки
5. **Деплой** бота реализован на сервере **Heroku**
6. Для общения с ботом реализован дружественный интерфейс на фреймворке **pyTelegramBotAPI**
7. Нейросетевые алгоритмы реализованы на фреймворке **pytorch**

   
### Структура кода
8. Диалог бота реализован в модуле **bot**
9. Алгоритмы стилизации **CycleGAN** и **NST** реализованы в соответствующих классах в модуле **models**
10. Пароли и токены задаются через переменные окружения
11. Для управления параметрами созданы конфигурационные и settings-файлы в соответствующих модулях

### Обучение нейросетей
12. Для алгоритмов **быстрой стилизации** с помощью нейросети **CycleGAN** было обучено **четыре** модели 
   на датасетах из картин художников. Обучение проводилось на сервисе **Google Colab**:
    - **Моне**, ноутбук с обучением модели [здесь]()
    - **Сезанн**, ноутбук с обучением модели [здесь]()
    - **Укиё-э**, ноутбук с обучением модели [здесь](https://colab.research.google.com/drive/1qDywo9sTxM625bgida4guqmbbQIqWnel?usp=sharing)
    - **Вангог**, ноутбук с обучением модели [здесь](https://colab.research.google.com/drive/1pDPV0p2_VXVHEdYBWQltJt8VXUDP_XFW?usp=sharing)

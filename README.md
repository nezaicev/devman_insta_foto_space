## Insta_foto_space
Скрипт обращаеться к API сервисов [[spasexdata.com]](https://spasexdata.com) и [[hubblesite.org]](https://hubblesite.org),
скачивает изображения и постит в Instagram.
Для запросов используется библиотека requests, для постов в Instagram, библиотека instabot.

##  Как  запустить
В системе должен быть установлен Python3

```bash
pip install -r requirements.txt
``` 

#### Переменные окружения
- INSTA_LOGIN
- INSTA_PASS

.env example:
```
INSTA_LOGIN=my_login
INSTA_PASS=my_pass
```
#### Запуск
Загрузка и постинг изображений с сервиса [[spasexdata.com]](https://spasexdata.com).
``` bash
$ python main.py -s

# Результат
Загрузка и постинг в ваш аккаунт изображений последнего вылета.
Если изображений в последнем вылете нет, то скрипт обращаеться к списку всех вылетов
```
Загрузка и постинг изображений с сервиса [[hubblesite.org]](https://hubblesite.org).
``` bash
$ python main.py -u hubble

# Вы получите
Введите название коллекции или ID изображения :
# Пример ввода
4573 - id изображения, загрузка и постинг одного изображения
news - название колекции, загрузка и постинг коллекции изображений
# Коллекции
"holiday_cards", "wallpaper", "spacecraft", "news", "printshop", "stsci_gallery"...
```
## Цель проекта 
Практика разработки на python

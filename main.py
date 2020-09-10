import os
import requests
import urllib3
import argparse

from PIL import Image
from instabot import Bot
from dotenv import load_dotenv

URL_SPACEX_LAUNCHES_LATEST = 'https://api.spacexdata.com/v3/launches/latest'
URL_SPACEX_LAUNCHES_ALL = 'https://api.spacexdata.com/v3/launches'
URL_HUBBLE = 'http://hubblesite.org/api/v3/'
IMAGE_DIRECTORY = 'image'


def download_img(url, name_img):
    urllib3.disable_warnings()
    result = requests.get(url, verify=False)
    result.raise_for_status()
    os.makedirs(IMAGE_DIRECTORY, exist_ok=True)
    with open(os.path.join(IMAGE_DIRECTORY, name_img), 'wb') as image:
        image.write(result.content)


def fetch_spacex_last_launch():
    response = requests.get(URL_SPACEX_LAUNCHES_LATEST)
    response.raise_for_status()
    response = response.json()
    collection_images = response['links']['flickr_images']
    if not collection_images:
        response = requests.get(URL_SPACEX_LAUNCHES_ALL)
        response.raise_for_status()
        launches = response.json()
        for launch in launches:
            if launch['links']['flickr_images']:
                collection_images = launch['links']['flickr_images']
    for index, url_img in enumerate(collection_images):
        download_img(url_img, 'spacex{}.jpg'.format(index))
        resize_img('spacex{}.jpg'.format(index))


def fetch_hubble_img(image_id):
    url_api_hubble = URL_HUBBLE + 'image/{}'.format(image_id)
    response = requests.get(url_api_hubble)
    response.raise_for_status()
    result = response.json()
    if result:
        url_img = "http:{}".format(result['image_files'][-1]['file_url'])
        file_name = '{}.{}'.format(image_id, get_extension_img(url_img))
        download_img(url_img, file_name)
        resize_img(file_name)
        return True
    else:
        return False


def get_extension_img(url):
    extension = url.split(".")[-1]
    return extension


def fetch_hubble_collection_img(name_collection):
    url_api_hubble = URL_HUBBLE + 'images/{}'.format(name_collection)
    response = requests.get(url_api_hubble)
    response.raise_for_status()
    images = response.json()
    if images:
        for img in images:
            fetch_hubble_img(img["id"])
            print("image:", img['id'], "ok")
        return True
    else:
        return False


def resize_img(file_name):
    try:
        image = Image.open((os.path.join(IMAGE_DIRECTORY, file_name)))
        image.thumbnail((1080, 1080))
        rgb_img = image.convert('RGB')
        rgb_img.save("{}/{}.jpg".format(IMAGE_DIRECTORY,
                                        file_name.split(".")[0]),
                     format="JPEG", )
    except Exception:
        raise EOFError


def post_img_in_insta(images, username, password):
    if images:
        bot = Bot()
        bot.login(username=username, password=password)
        for img in images:
            if os.path.splitext(img)[1] == '.jpg':
                bot.upload_photo(os.path.join(IMAGE_DIRECTORY, img))


def main():
    load_dotenv()
    username_insta = os.getenv('INSTA_LOGIN')
    password_insta = os.getenv('INSTA_PASS')
    parser = argparse.ArgumentParser(
        description="Скрипт скачивает изображения, используя API ресурсов "
                    "spasexdata.com и hubblesite.org и постит в Instagram."
    )
    parser.add_argument('-s',
                        '--spacex',
                        help='Запрос к API  spasexdata.com',
                        action='store_true', )
    parser.add_argument('-u',
                        '--hubble',
                        help='Запрос к API hubblesite.org',
                        action='store_true', )
    args = parser.parse_args()
    try:
        if args.spacex:
            fetch_spacex_last_launch()
            post_img_in_insta(images=os.listdir(IMAGE_DIRECTORY),
                              username=username_insta,
                              password=password_insta, )
        elif args.hubble:
            param = input("Введите название коллекции или ID изображения :")
            if param.isdigit():
                if fetch_hubble_img(param):
                    post_img_in_insta(images=os.listdir(IMAGE_DIRECTORY),
                                      username=username_insta,
                                      password=password_insta, )
                else:
                    print('Img not exist')
            else:
                if fetch_hubble_collection_img(param):
                    post_img_in_insta(images=os.listdir(IMAGE_DIRECTORY),
                                      username=username_insta,
                                      password=password_insta, )
                else:
                    print("Коллекция не существует")
        else:
            print("Выберите один из источников данных -s --spacex,-u --hubble")
    except requests.exceptions.HTTPError:
        print("Запрос к ресурсу завершился ошибкой")
    except EOFError:
        print("Не удается открыть файл")


if __name__ == "__main__":
    main()

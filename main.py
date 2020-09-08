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
    if not os.path.exists(IMAGE_DIRECTORY):
        os.makedirs(IMAGE_DIRECTORY)
    with open(os.path.join(IMAGE_DIRECTORY, name_img), 'wb') as f:
        f.write(result.content)


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
        print('Not img id - {}'.format(image_id))
        return False


def get_extension_img(url):
    extension = url.split(".")[-1]
    return extension


def fetch_hubble_collection_img(name_collection):
    url_api_hubble = URL_HUBBLE + 'images/{}'.format(name_collection)
    response = requests.get(url_api_hubble)
    response.raise_for_status()
    list_images = response.json()
    if list_images:
        for img in list_images:
            fetch_hubble_img(img["id"])
            print("image:", img['id'], "ok")
        return True
    else:
        print("Not images or not this collection")
        return False


def resize_img(file_name):
    try:
        image = Image.open((os.path.join(IMAGE_DIRECTORY, file_name)))
        image.thumbnail((1080, 1080))
        rgb_img = image.convert('RGB')
        rgb_img.save("{}/{}.jpg".format(IMAGE_DIRECTORY, file_name.split(".")[0]), format="JPEG")
    except Exception:
        print("File {} doesn't open".format(file_name))


def post_img_in_insta(list_images):
    if list_images:
        bot = Bot()
        bot.login(username=os.getenv('INSTA_LOGIN'), password=os.getenv('INSTA_PASS'))
        for img in list_images:
            if img.split('.')[-1] == 'jpg':
                bot.upload_photo(os.path.join(IMAGE_DIRECTORY, img))


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Скрипт скачивает изображения, используя API ресурсов spasexdata.com и hubblesite.org и постит в Instagram."
    )
    parser.add_argument('-r', '--resource', help='Название источника данных, пример (spacex)')
    args = parser.parse_args()

    try:
        if args.resource == 'spacex':
            fetch_spacex_last_launch()
        if args.resource == 'hubble':
            param = input("Введите название коллекции или ID изображения :")
            if param.isdigit():
                post_img_in_insta(os.listdir(IMAGE_DIRECTORY) if fetch_hubble_img(param) else print('Not fetch img'))
            else:
                post_img_in_insta(os.listdir(IMAGE_DIRECTORY) if fetch_hubble_collection_img(param) else print(
                    "Not fetch collection img"))

    except requests.exceptions.HTTPError:
        print("Запрос к ресурсу {}  завершился ошибкой".format(args.resource))


if __name__ == "__main__":
    main()

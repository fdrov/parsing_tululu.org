from pathlib import Path

import pathvalidate
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

id = 1


def check_for_redirect(response):
    if response.headers['Content-Type'] == 'text/html; charset=windows-1251':
        raise requests.exceptions.HTTPError('An HTTP error occurred')


def get_book_name(book_id):
    url = 'https://tululu.org/b'
    response = requests.get(url + str(book_id), verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    header_text = soup.find('body').find('h1').text
    title, author = header_text.split('::')
    return pathvalidate.sanitize_filename(title.strip())


def download_txt(url, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Ссылка на текст, который хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url, verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.exceptions.HTTPError as err:
        pass
    else:
        Path(f'{folder}').mkdir(parents=True, exist_ok=True)
        with open(f'{folder}{id}. {get_book_name(id)}.txt', 'wb') as book:
            book.write(response.content)


while id <= 10:
    download_txt('https://tululu.org/txt.php?id=' + str(id))
    id += 1

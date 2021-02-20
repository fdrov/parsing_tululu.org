import os
from pathlib import Path

import pathvalidate
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# url = 'https://tululu.org/b1/'
# response = requests.get(url, verify=False)
# response.raise_for_status()
# soup = BeautifulSoup(response.text, 'lxml')
# header_text = soup.find('body').find('h1').text
# title, author = header_text.split('::')
# print('Заголовок:', title.strip(), sep=' ')
# print('Автор:', author.strip(), sep=' ')

def check_for_redirect(response):
    if response.headers['Content-Type'] == 'text/html; charset=windows-1251':
        raise requests.exceptions.HTTPError('An HTTP error occurred')


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Ссылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    filename = pathvalidate.sanitize_filename(filename)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        Path(f'{folder}').mkdir(parents=True, exist_ok=True)
        with open(f'{folder}{filename}.txt', 'wb') as book:
            book.write(response.content)
    return f'{os.path.join(folder, filename)}.txt'


# Примеры использования
url = 'http://tululu.org/txt.php?id=1'

filepath = download_txt(url, 'Алиби')
print(filepath)  # Выведется books/Алиби.txt

filepath = download_txt(url, 'Али/би', folder='books/')
print(filepath)  # Выведется books/Алиби.txt

filepath = download_txt(url, 'Али\\би', folder='txt/')
print(filepath)  # Выведется txt/Алиби.txt

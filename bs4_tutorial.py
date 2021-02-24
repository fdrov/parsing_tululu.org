import os
import urllib.parse
from pathlib import Path

import pathvalidate
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_book_name(book_id):
    url = 'https://tululu.org/b'
    response = requests.get(url+str(book_id), verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    header_text = soup.find('body').find('h1').text
    pic_path = soup.find('div', class_='bookimage').find('img')['src']
    pic_url = urllib.parse.urljoin(url, pic_path)
    title, author = header_text.split('::')
    # print('Заголовок:', title.strip(), sep=' ')
    # print('Автор:', author.strip(), sep=' ')
    return {'title': pathvalidate.sanitize_filename(title.strip()), 'pic_url': pic_url }


def get_book_comment(book_id):
    url = 'https://tululu.org/b'
    response = requests.get(url+str(book_id), verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    header_text = soup.find('body').find('h1').text
    pic_path = soup.find('div', class_='bookimage').find('img')['src']
    pic_url = urllib.parse.urljoin(url, pic_path)
    comments = [comment.text for comment in soup.find('table', class_='tabs').find('td', class_='ow_px_td').find_all('span', class_='black')]
    title, author = header_text.split('::')
    genres = [genre.text for genre in soup.find('td', class_='ow_px_td').find('span', class_='d_book').find_all('a')]
    # print('Заголовок:', title.strip(), sep=' ')
    # print('Автор:', author.strip(), sep=' ')
    return {'title': pathvalidate.sanitize_filename(title.strip()), 'pic_url': pic_url, 'comments': comments, 'genres': genres}

print(get_book_comment(5))
# [print(value) for key, value in get_book_comment(5).items()]


exit()
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

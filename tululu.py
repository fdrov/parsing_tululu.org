import argparse
import logging
import sys
import urllib.parse
from pathlib import Path

import pathvalidate
import requests
import urllib3
from bs4 import BeautifulSoup


def main():
    logging.basicConfig(level=logging.INFO)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    book_url_pattern = 'https://tululu.org/b'
    book_txt_pattern = 'https://tululu.org/txt.php'

    parser = create_parser()
    namespace = parser.parse_args()

    for book_id in range(namespace.start_id, namespace.end_id + 1):
        response = requests.get(f'{book_url_pattern}{book_id}', verify=False)
        try:
            check_for_redirect(response)
            response.raise_for_status()
            book_page_info = parse_book_page(response)
            download_txt(book_id, book_txt_pattern, book_page_info)
            download_image(book_page_info['pic_url'])
            print(f'Заголовок: {book_page_info["title"]}', f'Автор: {book_page_info["author"]}', sep='\n')
            print()
        except requests.exceptions.HTTPError as err:
            print(err, book_id, file=sys.stderr)
            print(file=sys.stderr)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', default=1, nargs='?', type=int)
    parser.add_argument('end_id', default=10, nargs='?', type=int)
    return parser


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise_func_name = sys._getframe(1).f_code.co_name
        messages = {
            'main': 'Отсутствует на сайте книга id =',
            'download_txt': 'Ошибка скачивания текста книги id =',
            'download_image': 'Ошибка скачивания изображения книги id ='
        }
        raise requests.exceptions.HTTPError(messages.get(raise_func_name, 'HTTPError'))


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    h1_text = soup.find('body').find('h1').text
    title, author = h1_text.split('::')
    pic_path = soup.find('div', class_='bookimage').find('img')['src']
    pic_url = urllib.parse.urljoin(response.url, pic_path)
    comments = [comment.text for comment in soup.find('td', class_='ow_px_td').find_all('span', class_='black')]
    genres = [genre.text for genre in soup.find('td', class_='ow_px_td').find('span', class_='d_book').find_all('a')]
    return {
        'title': pathvalidate.sanitize_filename(title.strip()),
        'author': author.strip(),
        'img_src': pic_path,
        'pic_url': pic_url,
        'comments': comments,
        'genres': genres
    }


def download_image(pic_url, folder='images/'):
    response = requests.get(pic_url, verify=False)
    response.raise_for_status()
    Path(folder).mkdir(parents=True, exist_ok=True)
    pic_url_path = urllib.parse.unquote(urllib.parse.urlsplit(pic_url).path)
    img_name = pic_url_path.split('/')[-1]
    with open(f'{folder}{img_name}', 'wb') as img:
        img.write(response.content)


def download_txt(book_id, book_txt_pattern, book_page_info, folder='books/'):
    """Функция для скачивания текстовых файлов.

    Args:
        book_id (int): Ссылка на id книги, которую хочется скачать.
        book_txt_pattern (str): Шаблон URL для скачивания txt книги.
        book_page_info (dict): Словарь метаданных о книге.
        folder (str): Папка, куда сохранять. По-умолчанию 'books/'

    Returns:
        None
    """
    payload = {'id': book_id}
    response = requests.get(book_txt_pattern, params=payload, verify=False)
    check_for_redirect(response)
    response.raise_for_status()
    Path(f'{folder}').mkdir(parents=True, exist_ok=True)
    with open(f'{folder}{book_id}. {book_page_info["title"]}.txt',
              'w',
              encoding='UTF-8') as book:
        book.write(response.text)


if __name__ == '__main__':
    main()

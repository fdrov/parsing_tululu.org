import urllib.parse
from pathlib import Path

import pathvalidate
import requests
import urllib3
from bs4 import BeautifulSoup
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

book_url_pattern = 'https://tululu.org/b'
book_txt_pattern = 'https://tululu.org/txt.php?id='


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', default=1, nargs='?', type=int)
    parser.add_argument('end_id', default=10, nargs='?', type=int)
    return parser


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.HTTPError('An HTTP error occurred')


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    h1_text = soup.find('body').find('h1').text
    title, author = h1_text.split('::')
    pic_path = soup.find('div', class_='bookimage').find('img')['src']
    pic_url = urllib.parse.urljoin(response.url, pic_path)
    comments = [comment.text for comment in soup.find('td', class_='ow_px_td').find_all('span', class_='black')]
    genres = [genre.text for genre in soup.find('td', class_='ow_px_td').find('span', class_='d_book').find_all('a')]
    return {'title': pathvalidate.sanitize_filename(title.strip()), 'author': author.strip(), 'pic_url': pic_url, 'comments': comments, 'genres': genres}


def download_image(pic_url, folder='images/'):
    response = requests.get(pic_url, verify=False)
    Path(f'{folder}').mkdir(parents=True, exist_ok=True)
    img_name = urllib.parse.unquote(urllib.parse.urlsplit(pic_url).path.split('/')[-1])
    with open(f'{folder}{img_name}', 'wb') as img:
        img.write(response.content)


def download_txt(id, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Ссылка на id книги, которую хочется скачать.
        folder (str): Папка, куда сохранять.
    """
    response = requests.get(book_txt_pattern + str(id), verify=False)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.exceptions.HTTPError as err:
        pass
    else:
        Path(f'{folder}').mkdir(parents=True, exist_ok=True)
        with open(f'{folder}{id}. {book_page_info["title"]}.txt', 'wb') as book:
            book.write(response.content)

parser = create_parser()
namespace = parser.parse_args()

for id in range(namespace.start_id, namespace.end_id + 1):
    response = requests.get(book_url_pattern + str(id), verify=False)
    try:
        check_for_redirect(response)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        pass
    else:
        book_page_info = parse_book_page(response)
        # print(book_page_info['title'])
        print(f'Заголовок: {book_page_info["title"]}', f'Автор: {book_page_info["author"]}', '', sep='\n')
        download_txt(id)
        download_image(book_page_info['pic_url'])
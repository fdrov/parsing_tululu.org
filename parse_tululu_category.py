import argparse
import json
import posixpath
import sys
import urllib
from pathlib import Path

import pathvalidate
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BOOK_CATEGORY = 'https://tululu.org/l55/'
VHOST = 'https://tululu.org'
BOOK_DOWNLOAD_PATTERN = 'https://tululu.org/txt.php'
BOOK_PAGE_PATTERN = 'https://tululu.org/b'
IMAGES_FOLDER = 'images'
BOOKS_FOLDER = 'books'
catalogue = []


def main():
    last_page = get_last_category_page(BOOK_CATEGORY)

    parser = argparse.ArgumentParser(
        description='Этот скрипт скачает книги и изображения')
    parser.add_argument('--start_page', type=int,
                        default=1,
                        help='Начальная страница', )
    parser.add_argument('--end_page', type=int,
                        default=last_page + 1,
                        help='Страница, перед которой остановить парсинг', )
    parser.add_argument('--dest_folder',
                        default='',
                        help='Путь к каталогу с результатами парсинга')
    parser.add_argument('--skip_imgs', action='store_true',
                        help='не скачивать картинки', )
    parser.add_argument('--skip_txt', action='store_true',
                        help='не скачивать книги', )
    parser.add_argument('--json_path',
                        default='',
                        help='указать свой путь к *.json файлу с результатами',)
    # args = parser.parse_args() # for production
    args = parser.parse_args(
        '--start_page 1 --end_page 2 --dest_folder destfolder --json_path jsonfolder'.split()
    )  # for cozy testing
    print(args)
    global skip_imgs, skip_txt
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    for page_number in range(args.start_page, args.end_page):
        book_category_paginated = urllib.parse.urljoin(BOOK_CATEGORY,
                                                       str(page_number))
        response = requests.get(book_category_paginated, verify=False)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            print('Начинаю парсить страницу = ', page_number)
            pars_books_from_page(response, args.dest_folder)
        except requests.exceptions.HTTPError as err:
            print(err, file=sys.stderr)
    write_books_meta_to_json(catalogue, args.dest_folder, args.json_path)


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise_func_name = sys._getframe(1).f_code.co_name
        messages = {
            'main': 'Отсутствует на сайте книга id =',
            'download_txt': 'Ошибка скачивания текста книги id =',
            'download_image': 'Ошибка скачивания изображения книги id ='
        }
        raise requests.exceptions.HTTPError(
            messages.get(raise_func_name, 'HTTPError'))


def write_books_meta_to_json(books_meta_raw, base_save_path, json_path):
    full_path = posixpath.join(base_save_path, json_path, '')
    Path(full_path).mkdir(parents=True, exist_ok=True)
    with open(f'{full_path}books.json', 'w', encoding='UTF-8') as json_file:
        json.dump(books_meta_raw, json_file, ensure_ascii=False, indent=2)


def get_last_category_page(category_url):
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.center .npage'
    last_page = soup.select(selector)[-1].text
    return int(last_page)


def parse_book_page(book_id):
    book_url = f'{BOOK_PAGE_PATTERN}{book_id}'
    response = requests.get(book_url, verify=False)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err, file=sys.stderr)
    soup = BeautifulSoup(response.text, 'lxml')
    h1_text = soup.select_one('body h1').text
    title, author = h1_text.split('::')
    pic_url = soup.select_one('.bookimage img')['src']
    comments = [comment.text for comment in soup.select('.ow_px_td .black')]
    genres = [genre.text for genre in soup.select('.ow_px_td span.d_book a')]
    book_meta_info = {
        'title': pathvalidate.sanitize_filename(title.strip()),
        'author': author.strip(),
        'img_src': '',
        'book_path': '',
        'comments': comments,
        'genres': genres
    }
    return book_meta_info, pic_url


def pars_books_from_page(response, base_save_path):
    soup = BeautifulSoup(response.text, features='lxml')
    selector = '.ow_px_td .bookimage a'
    books_listing_raw = soup.select(selector)
    for book_tag in books_listing_raw:
        book_id = book_tag['href'].strip('/b')
        book_meta_info, pic_url = parse_book_page(book_id)
        if download_txt(book_id, book_meta_info, base_save_path):
            download_image(pic_url, book_meta_info, base_save_path)
            catalogue.append(book_meta_info)


def download_txt(book_id, book_meta_info, base_save_path):
    """Функция для скачивания текстовых файлов.

    Args:
        book_id (int): Ссылка на id книги, которую хочется скачать.
        book_meta_info (dict): Словарь метаданных о книге.
        base_save_path (str): Путь к каталогу с папкой books

    Returns:
        None
    """
    payload = {'id': book_id}
    response = requests.get(BOOK_DOWNLOAD_PATTERN, params=payload, verify=False)
    try:
        check_for_redirect(response)
        if not skip_txt:
            txt_full_path = posixpath.join(base_save_path, BOOKS_FOLDER, '')
            Path(txt_full_path).mkdir(parents=True, exist_ok=True)
            filename = f'{txt_full_path}{book_meta_info["title"]}.txt'
            with open(filename, 'w', encoding='UTF-8') as book:
                book.write(response.text)
            book_path = posixpath.join(txt_full_path,
                                       f'{book_meta_info["title"]}.txt')
            book_meta_info['book_path'] = book_path
            print('Книга скачена', book_id)
    except requests.exceptions.HTTPError as err:
        print(err, book_id)
        return False
    return True


def download_image(img_relative_src, book_meta_info, base_save_path):
    if not skip_imgs:
        pic_absolute_url = urllib.parse.urljoin(VHOST, img_relative_src)
        response = requests.get(pic_absolute_url, verify=False)
        response.raise_for_status()
        image_full_path = posixpath.join(base_save_path, IMAGES_FOLDER, '')
        Path(image_full_path).mkdir(parents=True, exist_ok=True)
        img_name = posixpath.basename(pic_absolute_url)
        with open(f'{image_full_path}{img_name}', 'wb') as img:
            img.write(response.content)
        book_meta_info['img_src'] = posixpath.join(image_full_path, img_name)


if __name__ == '__main__':
    main()

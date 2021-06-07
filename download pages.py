import argparse
import json
import os
import sys
import urllib
from pathlib import Path

import pathvalidate
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
book_category = 'https://tululu.org/l55/'
vhost = 'https://tululu.org'
book_download_pattern = 'https://tululu.org/txt.php'
book_page_pattern = 'https://tululu.org/b'
images_folder = 'images/'
books_folder = 'books/'
catalogue = []


def main():
    last_page = get_last_category_page(book_category)

    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', type=int, nargs='?')
    parser.add_argument('--end_page', type=int, nargs='?', default=last_page)
    args = parser.parse_args(
        '--start_page 1 --end_page 4'.split())  # TODO delete text into brackets to use script manually
    print(args)

    for page_number in range(args.start_page, args.end_page + 1):
        book_category_paginated = urllib.parse.urljoin(book_category,
                                                       str(page_number))
        response = requests.get(book_category_paginated, verify=False)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            print('Начинаю парсить страницу = ', page_number)
            pars_books_from_page(response)
        except requests.exceptions.HTTPError as err:
            print(err, file=sys.stderr)
    write_books_meta_to_json(catalogue)


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


def write_books_meta_to_json(books_meta_raw):
    with open('books.json', 'w', encoding='UTF-8') as json_file:
        json.dump(books_meta_raw, json_file, ensure_ascii=False, indent=2)


def get_last_category_page(category_url):
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, 'lxml')
    last_page = soup.find('p', class_='center').find_all('a', class_='npage')[
        -1].text
    return last_page


def parse_book_page(book_id):
    book_url = f'{book_page_pattern}{book_id}'
    response = requests.get(book_url, verify=False)
    try:
        response.raise_for_status()
        check_for_redirect(response)
    except requests.exceptions.HTTPError as err:
        print(err, file=sys.stderr)
    soup = BeautifulSoup(response.text, 'lxml')
    h1_text = soup.find('body').find('h1').text
    title, author = h1_text.split('::')
    pic_path = soup.find('div', class_='bookimage').find('img')['src']
    pic_url = os.path.join(images_folder, os.path.basename(pic_path))
    comments = [comment.text for comment in
                soup.find('td', class_='ow_px_td').find_all('span',
                                                            class_='black')]
    genres = [genre.text for genre in
              soup.find('td', class_='ow_px_td').find('span',
                                                      class_='d_book').find_all(
                  'a')]
    book_meta_info = {
        'title': pathvalidate.sanitize_filename(title.strip()),
        'author': author.strip(),
        'img_src': pic_url,
        'comments': comments,
        'genres': genres
    }
    return book_meta_info, pic_path


def pars_books_from_page(response):
    soup = BeautifulSoup(response.text, features='lxml')
    selector = '.ow_px_td .bookimage a'
    books_listing_raw = soup.select(selector)
    for book_tag in books_listing_raw:
        book_id = book_tag['href'].strip('/b')
        book_meta_info, pic_path = parse_book_page(book_id)
        if download_txt(book_id, book_meta_info):
            download_image(pic_path)
            catalogue.append(book_meta_info)


def download_txt(book_id, book_meta_info):
    """Функция для скачивания текстовых файлов.

    Args:
        book_id (int): Ссылка на id книги, которую хочется скачать.
        book_meta_info (dict): Словарь метаданных о книге.

    Returns:
        None
    """
    # is_txt_downloaded = False
    payload = {'id': book_id}
    response = requests.get(book_download_pattern, params=payload, verify=False)
    try:
        check_for_redirect(response)
        response.raise_for_status()
        Path(f'{books_folder}').mkdir(parents=True, exist_ok=True)
        with open(f'{books_folder}{book_id}. {book_meta_info["title"]}.txt',
                  'w',
                  encoding='UTF-8') as book:
            book.write(response.text)
        print('Книга скачена', book_id)
    except requests.exceptions.HTTPError as err:
        print(err, book_id)
        return False
    return True


def download_image(img_src):
    pic_url = urllib.parse.urljoin(vhost, img_src)
    response = requests.get(pic_url, verify=False)
    response.raise_for_status()
    Path(images_folder).mkdir(parents=True, exist_ok=True)
    img_name = os.path.basename(pic_url)
    with open(f'{images_folder}{img_name}', 'wb') as img:
        img.write(response.content)


if __name__ == '__main__':
    main()

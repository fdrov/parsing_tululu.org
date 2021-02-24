import urllib.parse
from pathlib import Path

import pathvalidate
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

id = 1
book_url_pattern = 'https://tululu.org/b'


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
    return {'title': pathvalidate.sanitize_filename(title.strip()), 'pic_url': pic_url, 'comments': comments, 'genres': genres}


# def download_image(pic_url, folder='images/'):
#     response = requests.get(pic_url, verify=False)
#     Path(f'{folder}').mkdir(parents=True, exist_ok=True)
#     img_name = urllib.parse.unquote(urllib.parse.urlsplit(pic_url).path.split('/')[-1])
#     with open(f'{folder}{img_name}', 'wb') as img:
#         img.write(response.content)


# def download_txt(url, folder='books/'):
#     """Функция для скачивания текстовых файлов.
#     Args:
#         url (str): Ссылка на текст, который хочется скачать.
#         folder (str): Папка, куда сохранять.
#     Returns:
#         str: Путь до файла, куда сохранён текст.
#     """
#     response = requests.get(url, verify=False)
#     response.raise_for_status()
#     try:
#         check_for_redirect(response)
#     except requests.exceptions.HTTPError as err:
#         pass
#     else:
#         Path(f'{folder}').mkdir(parents=True, exist_ok=True)
#         book_info = parse_book_page(id)
#         download_image(book_info["pic_url"])
#         with open(f'{folder}{id}. {book_info["title"]}.txt', 'wb') as book:
#             book.write(response.content)
#         print(f'Заголовок: {book_info["title"]}', book_info["pic_url"], book_info["comments"], book_info["genres "], '', sep='\n')


while id <= 3:
    response = requests.get(book_url_pattern + str(id), verify=False)
    try:
        check_for_redirect(response)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        pass
    else:
        book_page_info = parse_book_page(response)
        # print(book_page_info['title'])
        print(f'Заголовок: {book_page_info["title"]}', book_page_info["pic_url"], book_page_info["comments"], book_page_info["genres"], '', sep='\n')

    id += 1

from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Path("./books").mkdir(parents=True, exist_ok=True)
url = 'https://tululu.org/txt.php?id='
id = 1


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


while id <= 10:
    response = requests.get(url + str(id), verify=False)
    response.raise_for_status()
    print(f'Id = {id} has http-status : {response.status_code} and Content-Type : {response.headers["Content-Type"]}')

    try:
        check_for_redirect(response)
    except requests.exceptions.HTTPError:
        print(f'EXEPTION at Id = {id}')
        id += 1
        continue

    with open(f'./books/id{id}.txt', 'wb') as book:
        book.write(response.content)

    id += 1

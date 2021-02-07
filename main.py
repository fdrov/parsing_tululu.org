import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Path("./books").mkdir(parents=True, exist_ok=True)

url = 'https://tululu.org/txt.php?id='


id = 1

while id < 11:
    response = requests.get(url + str(id), verify=False)
    response.raise_for_status()
    print(f'Id = {id} has http-status : {response.status_code} and Content-Type : {response.headers["Content-Type"]}')

    with open(f'./books//id{id}.txt', 'wb') as book:
        book.write(response.content)
    id +=1

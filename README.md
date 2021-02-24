# Парсер книг с сайта tululu.org

Скрипт выведет информацию о книге (название, автор, коментарии, жанр) с сайта [tululu.org](https://tululu.org/). Также, скачает саму книгу и обложку. 

### Как установить
Для запуска:
* должен быть установлени Python 3.8 и выше.
* библиотеки из файла requirements.txt (установить можно командой ```pip install -r requirements.txt```)

### Как запустить

Ввести в командной строке python `tululu.py`

В результате вы увидите следующее:
```
>>> python tululu.py

…\tululu.py
Заголовок: Административные рынки СССР и России
Автор: Кордонский Симон

Заголовок: Азбука экономики
Автор: Строуп Р

Заголовок: Азиатский способ производства и Азиатский социализм
Автор: Прохоренко Иван Денисович

Заголовок: Бал хищников
Автор: Брук Конни

Заголовок: Бархатная революция в рекламе
Автор: Зимен Сержио
…
```

### Аргументы
По умолчанию, скрипт скачает книги с id 1 по 10 включительно.
Чтобы задать диапазон скачивания вручную, нужно задать позиционные аргументы `start_page` и `end_page` — страница начала и конца парсинга, соответстенно.
Например, чтобы скачать книги с 10 по 20 введите `tululu.py 10 20`

### Сохранение книги и обложки

По умолчанию, книги сохраняются в папку `books/`, а обложки в `images/` в папке расположения скрипта `tululu.py`.

### Вывод информации о книге

По мере скачивания, скрипт выводит *Название книги* и *Автора*.
Также, есть возможность вывести Коммертарии и Жанр.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).


# homework_bot

```
Телеграм-бот для отслеживания статуса код-ревью.
Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.
```

### Технологии:
- Python 3.7
- python-dotenv 0.19.0
- python-telegram-bot 13.7

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/LikeNo0ther/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
py -m venv venv
```

```
source venv/activate
```

Установить зависимости из файла requirements.txt:

```
py -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Записать в переменные окружения (файл .env) необходимые ключи:
- токен профиля
- токен телеграм-бота
- свой ID в телеграме

Выполнить миграции:

```
py manage.py migrate
```

Запустить проект:

```
py manage.py runserver
```

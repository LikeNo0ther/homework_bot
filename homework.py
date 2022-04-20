import logging
import os
import time
from http import HTTPStatus
import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class Important_Exception(Exception):
    pass


def exception_logging_eror(message):
    logger.error(message)
    raise Important_Exception(message)


def exception_logging_critical(message):
    logger.critical(message)
    raise Important_Exception(message)


def send_message(bot, message):
    """Отправка сообщения в Телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение в чат {TELEGRAM_CHAT_ID}: {message}')
    except Exception:
        logger.error('Ошибка отправки сообщения')


def get_api_answer(current_timestamp):
    """Запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != HTTPStatus.OK:
            exception_logging_eror(f'Возникла ошибка: {response}')
        return response.json()
    except Exception:
        exception_logging_eror('Ошибка запроса к API')


def check_response(response):
    """Проверка ответа API-сервиса на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')
    try:
        homeworks = response['homeworks']
    except KeyError:
        exception_logging_eror('Ошибка обращения по ключу')
    try:
        homework = homeworks[0]
    except IndexError:
        exception_logging_eror('Нет выполненных работ')
    return homework


def parse_status(homework):
    """Извлечение статуса конкретной работы."""
    if 'homework_name' not in homework:
        raise KeyError
    if 'status' not in homework:
        raise Exception
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        exception_logging_eror(f'Пришел новый статус: {homework_status}')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        exception_logging_critical('Отсутствует(ют) переменная(ые) окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    CURRENT_STATUS = ''
    MESSAGE_ERROR = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            message = parse_status(check_response(response))
            if message != CURRENT_STATUS:
                send_message(bot, message)
                CURRENT_STATUS = message
        except Exception as error:
            logger.error('Возникла ошибка')
            message = str(error)
            if message != MESSAGE_ERROR:
                send_message(bot, message)
                MESSAGE_ERROR = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

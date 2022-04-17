import json
# для корректного переноса времени сообщений в json
import time
from datetime import datetime

from telethon.sync import TelegramClient
# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

# # Считываем учетные данные
# config = configparser.ConfigParser()
# config.read("config.ini")
#
# # Присваиваем значения внутренним переменным
# api_id = config['Telegram']['api_id']
# api_hash = config['Telegram']['api_hash']
# username = config['Telegram']['username']
import app_ui
# классы для работы с каналами
import parse_handler

telethon_data = {
    "client": None,
    "api_id": None,
    "api_hash": None,
    "username": None,
    "phone": None,

    # Тип str обязателен
    "code": None
}


async def dump_all_messages(channel, date_from, handler: parse_handler.ParseHandler):
    client: TelegramClient = telethon_data["client"]

    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0  # номер записи, с которой начинается считывание
    limit_msg = 100  # максимальное число записей, передаваемых за один раз

    all_messages = []  # список всех сообщений
    total_messages = 0
    total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

    class DateTimeEncoder(json.JSONEncoder):
        """Класс для сериализации записи дат в JSON"""

        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    # Можно делать 30 запросов за 30 секунд

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages

        current_date = app_ui.date_to_string(
            messages[0].date.year,
            messages[0].date.month,
            messages[0].date.day
        )

        if current_date < date_from:
            break

        for message in messages:
            all_messages.append(message.to_dict())
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        print(total_messages)

        info: str = 12 * ' ' + f'Найдено {total_messages} постов.'
        if total_messages <= 100:
            handler.add_debug(info)
        else:
            handler.change_posts_info(info)

        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

        time.sleep(1)

    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)

import asyncio
import sys
import traceback

from PyQt5.QtWidgets import QApplication
from telethon import TelegramClient

import app_ui
import morph
from morph import search
from tg_parser import telethon_data, dump_all_messages
from to_excel import save_all_channels


def main():
    app = QApplication(sys.argv)
    window = app_ui.MainWindow()
    window.show()
    sys.exit(app.exec_())


async def parse(data, handler):
    # Проверка правильности запроса

    try:
        message = "Проверка правильности запроса."
        is_in = lambda word, message: str(word) in message
        exec(morph.normalize_request(data["request"]))
        handler.add_debug("Запрос введён корректно.")

    except SyntaxError:
        handler.add_debug("Некорректный запрос.\n"
                          "Используйте инструкцию "
                          "(знак вопроса справа от поля ввода "
                          "ключевых слов).")
        handler.thread.terminate()
        return

    handler.add_debug("Запуск")
    try:
        print("Connecting...")
        handler.add_debug("Установка соединения...")
        telethon_data["client"] = TelegramClient(
            telethon_data["username"],
            int(telethon_data["api_id"]),
            telethon_data["api_hash"]
        )
        await telethon_data["client"].start()
    except:
        handler.add_debug(traceback.format_exc())

    print("Connected. Starting search.")
    handler.add_debug("Соединение установлено.\nНачало поиска.")
    channels_with_messages = {}
    try:
        for link in data["links"]:
            try:
                handler.add_debug(4 * ' ' + "Текущий канал: {}".format(link))

                channel = await telethon_data["client"].get_entity(link)

                handler.add_debug(8 * ' ' + "Канал найден. Скачиваем все посты...")

                await dump_all_messages(channel, data["date_from"])

                handler.add_debug(8 * ' ' + "Посты скачаны. Начинаем поиск ключевых слов.")

                list_of_posts = await (search(data["request"], data["date_from"], data["date_to"]))

                handler.add_debug(12 * ' ' + "Найдено подходящих постов: {}.".format(len(list_of_posts)))

                channels_with_messages[link] = list_of_posts

            except ValueError:
                handler.add_debug(4 * ' ' + "Канал {} не найден.".format(link))
    except:
        handler.add_debug(traceback.format_exc())
    finally:
        if telethon_data["client"] is not None and telethon_data["client"].is_connected():
            await telethon_data["client"].disconnect()
            print("Disconnected.")

    save_all_channels(channels_with_messages, "result.xlsx")

    handler.add_debug("Поиск завершен.\n")
    handler.thread.terminate()


def start(data, handler):
    asyncio.run(parse(data, handler))


if __name__ == "__main__":
    main()

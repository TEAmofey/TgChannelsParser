import asyncio
import re
import traceback
import app_ui
import sys
from telethon import TelegramClient
from tg_parser import telethon_data, dump_all_messages
from exceptions import RequestException, SearchException
from morph import search
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    window = app_ui.MainWindow()
    window.show()
    sys.exit(app.exec_())


async def parse(data, handler):
    try:
        print("Connecting...")
        handler.add_debug("Установка соединения...")
        telethon_data["client"] = TelegramClient(
            telethon_data["username"],
            int(telethon_data["api_id"]),
            telethon_data["api_hash"])
        await telethon_data["client"].start()
    except:
        handler.add_debug(traceback.format_exc())

    print("Connected. Starting search.")
    handler.add_debug("Соединение установлено.\nНачало поиска.")
    for link in data["links"]:
        try:
            handler.add_debug(4 * ' ' + "Текущий канал: {}".format(link))

            channel = await telethon_data["client"].get_entity(link)

            handler.add_debug(8 * ' ' + "Канал найден. Скачиваем все посты...")

            await dump_all_messages(channel)

            handler.add_debug(8 * ' ' + "Посты скачаны. Начинаем поиск ключевых слов.")

            dicts_of_posts = await (search(data["request"], data["date_from"], data["date_to"]))

            handler.add_debug(12 * ' ' + "Найдено подходящих постов: {}.".format(len(dicts_of_posts)))

        except SearchException:
            handler.add_debug("Произошла ошибка")
        except RequestException as e:
            handler.add_debug("Неправильный запрос.\nИспользуйте инструкцию (знак вопроса справа от поля ввода "
                              "ключевых слов).")
        except ValueError:
            handler.add_debug(4 * ' ' + "Канал {} не найден.".format(link))
        except:
            handler.add_debug(traceback.format_exc())

    if telethon_data["client"] is not None and telethon_data["client"].is_connected():
        await telethon_data["client"].disconnect()
        # handler.add_debug("Disconnected.")

    handler.add_debug("Поиск завершен.")


def start(data, handler):
    asyncio.run(parse(data, handler))


if __name__ == "__main__":
    main()

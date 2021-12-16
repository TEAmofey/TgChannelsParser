from tg_parser import client
from tg_parser import dump_all_messages
from app_ui import application
from morph import search


async def main():
    url = input("Введите ссылку на канал или чат: ")
    channel = await client.get_entity(url)
    req = input("Введите запрос: ")
    # await dump_all_messages(channel)
    results = await search(req, [channel])
    if results:
        print(results)
    #     for x in results[1]:
    #         print(x)
    else:
        print("Nothing")
with client:
    client.loop.run_until_complete(main())


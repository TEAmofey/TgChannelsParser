import pymorphy2
import re
from exceptions import SearchException, RequestException
from traceback import print_stack, print_exc
import datetime

from tg_parser import dump_all_messages, client
from parse_json import parse

# Создаем объект класса-анализатора
morph = pymorphy2.MorphAnalyzer()

''' функция приведения слова в начальную форму '''


# пробуем просклонять в единственное число и именительный падеж
# если просклонять не удалось, morph вернет None
# если вернулось не None, то вернем получившееся слово, иначе -- исходное
def normalize_word(word):
    normalizedWord = morph.parse(word)[0].normal_form

    if normalizedWord:
        return normalizedWord
    return word


''' функция приведения всех слов в сообщении в начальную форму '''


# разбиваем сообщение на слова, проходимся по каждому слову (здесь w -- слово, i -- его индекс в массиве),
# с помощью регулярного выражения убираем из слова все лишнее (все символы, кроме букв и цифр), переводим в lowercase,
# закидываем наше "очищенное" слово в нормализатор и записываем результат в массив,
# возвращаем frozenset, т.к. одинаковые слова нам не нужны

def normalize_message(message):
    message = re.sub(r'[^A-Za-zА-яёЁ0-9]', ' ', message)
    message = message.split(' ')
    for i, w in enumerate(message):
        message[i] = normalize_word(w)
    message = set(message)
    return message


''' функция приведения к нормальному виду пользовательского запроса'''


def normalize_request(req):
    """
    @DOCUMENTATION:
        1. в пользовательском запросе должно выполняться правило: один оператор -- два операнда (слова),
        то есть, если нужно искать "президент Казахстана", то запрос должен иметь следующий вид:
        президент & Казахстана
        иначе, при вводе "президент Казахстана", поиск будет производиться по "президентказахстана"
    """
    req = req.replace(' ', '')  # сначала убираем из запроса все пробелы
    req = req.replace('&', " and ")  # меняем операторы "и" и "или" на то, что сможет считать питон
    req = req.replace('|', " or ")
    req = req.replace('(', " ( ")  # ставим пробелы около скобок, чтобы впоследствии трактовать их как отдельное слово
    req = req.replace(')', " ) ")
    req = re.sub(r'[^А-яёЁA-Za-z0-9-\s()]', '',
                 req)  # выбрасываем из строки все символы, кроме букв, цифр, скобок, пробелов и дефисов
    req = req.split(' ')  # разбиваем на "слова"

    ''' 
    эта часть работает -- значит лучше не трогать, лол.
    на самом деле, я не придумал, как можно реализовать это по-человечески, но здесь суть в том,
    что мы приводим нашу стрингу с запросом к такому виду, чтобы можно было интерпретировать ее как строчку кода.
    интерпретировать будем как лямбда-функцию, которую определим дальше
    '''
    for i, w in enumerate(req):
        if w in ["and", "or", '(', ')', '']:
            continue
        req[i] = "is_in(\"" + normalize_word(w) + "\", message)"

    return "global res; res = " + ' '.join(req)


''' функция, проверяющая, есть ли в сообщении нужное слово'''

""" 
ВАЖНО: здесь функция получает уже нормализованный request (т.е. прогнанный через normalize_request)
"""


# нормализуем сообщение через определенные раннее функции;
# дефайним нашу замечательную лямбду;
# выполняем request как строчку кода, после чего получаем в res True или False,
# в зависимости от того, успешен ли запрос
def is_suitable(request, message):
    is_in = lambda word, message: str(word) in message
    global res
    res = None
    try:
        exec(request)
    except SyntaxError:
        raise RequestException(request)
    return res


''' Функция поиска запроса по списку каналов. Возвращает словарь  вида
    {"channel" : posts}, где posts -- массив всех подходящих постов,
    каждый из которых представлен в виде словаря {"message": msg, "date": time_stamp} '''


async def search(request, date_from, date_to):
    request = normalize_request(request)

    try:
        suitable_messages = []
        posts = parse("channel_messages.json", date_from, date_to)

        for post in posts:
            if "message" in post.keys():
                msg = normalize_message(post["message"])
                if is_suitable(request, msg):
                    suitable_messages.append(post)

        return suitable_messages
    except RequestException as error:
        raise RequestException(error.request)

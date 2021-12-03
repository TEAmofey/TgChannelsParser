import pymorphy2
import re

# Создаем объект класса-анализатора
morph = pymorphy2.MorphAnalyzer()

''' функция приведения слова в начальную форму '''


# пробуем просклонять в единственное число и именительный падеж
# если просклонять не удалось, morph вернет None 
# если вернулось не None, то вернем получившееся слово, иначе -- исходное
def normalize_word(word):
    normalizedWord = morph.parse(word)[0].inflect({"sing", "nomn"})

    if normalizedWord:
        return normalizedWord.word
    return word


''' функция приведения всех слов в сообщении в начальную форму '''


# разбиваем сообщение на слова, проходимся по каждому слову (здесь w -- слово, i -- его индекс в массиве),
# с помощью регулярного выражения убираем из слова все лишнее (все символы, кроме букв и цифр), переводим в lowercase,
# закидываем наше "очищенное" слово в нормализатор и записываем результат в массив,
# возвращаем frozenset, т.к. одинаковые слова нам не нужны

def normalize_message(message):
    message = message.split(' ')
    for i, w in enumerate(message):
        w = re.sub(r'[^A-Za-zА-яёЁ0-9]', '', w).lower()
        message[i] = normalize_word(w)
    return frozenset(message)


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
    message = normalize_message(message)
    is_in = lambda word, message: str(word) in message
    global res
    res = None
    exec(request)
    return res
class RequestException(Exception):
    def __init__(self, request, message="Probably incorrect request"):
        self.request = request
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.request} -> {self.message}'


class SearchException(Exception):
    pass

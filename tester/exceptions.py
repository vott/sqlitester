class ImproperlyConfigured(Exception):
    def __init__(self, message):
        _message = f'Missing parameter {message}'
        super().__init__(_message)


class EmptyWebPage(Exception):
    def __init__(self, url):
        _message = f'Missing parameter {message}'
        super().__init__(_message)
class ImproperlyConfigured(Exception):
    def __init__(self, message):
        _message = 'Missing parameter {}'.format(message)
        super().__init__(_message)


class EmptyWebPage(Exception):
    pass
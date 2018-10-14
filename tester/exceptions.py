class ImproperlyConfigured(Exception):
    def __init__(self, message):
        _message = f'Missing parameter {message}'
        super().__init__(_message)
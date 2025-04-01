import requests


class HttpError(Exception):
    def __init__(self, message: str, response_str: str, response_obj: requests.Response):
        super().__init__(message)
        self.message = message
        self.response_str = response_str
        self.response_obj = response_obj

    def __str__(self):
        return f"{self.message} [{self.response_obj.status_code}]"


class NotFoundError(HttpError):
    pass


class AntiBotBlockError(HttpError):
    pass


class UnauthorizedError(HttpError):
    pass

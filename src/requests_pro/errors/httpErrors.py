import requests


class HttpError(Exception):
    def __init__(
        self, message: str, response_str: str, response_obj: requests.Response
    ):
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


class GroupedError(ExceptionGroup):
    def __new__(cls, message: str, errors: list[Exception]):
        return super().__new__(cls, message, errors)

    def __str__(self):
        message = f"{self.args[0]}\n"
        for index, error in enumerate(self.exceptions):
            message += f"{index}. [{error.__class__.__name__}]: {error}\n"
        return message

    def get_last_error(self):
        return self.exceptions[-1] if self.exceptions else None  # Avoid indexing error


class RequestsGroupedError(GroupedError):
    pass

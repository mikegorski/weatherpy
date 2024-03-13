class BadRequest(Exception):
    """Exception class for handling OpenWeather API bad requests."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return f"Code {self.code}: {self.message.title()}"

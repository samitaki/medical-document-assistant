class ServiceError(Exception):
    """Something the user needs to read, not a traceback. Routes turn it into a json error."""

    def __init__(self, message: str, status: int = 503):
        super().__init__(message)
        self.message = message
        self.status = status

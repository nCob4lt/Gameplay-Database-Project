from datetime import datetime

class DataNotFound(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.timestamp = datetime.now()
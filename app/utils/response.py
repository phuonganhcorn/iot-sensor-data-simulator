class Response:
    def __init__(self, success, message="", object=None):
        self.success = success
        self.message = message
        self.object = object
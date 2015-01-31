class ValidationError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def message_to_dict(self):
        message = {}
        message['status'] = self.status_code
        message['message'] = self.message
        return message


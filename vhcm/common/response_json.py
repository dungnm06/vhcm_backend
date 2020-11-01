class ResponseJSON(object):
    def __init__(self, status=False, messages=None, result_data=None):
        if messages is None:
            messages = []
        self.status = status
        self.messages = messages
        self.result_data = result_data

    def to_json(self):
        return {
            'status': self.status,
            'messages': self.messages,
            'result_data': self.result_data
        }

    def set_status(self, status):
        self.status = status

    def set_messages(self, messages):
        if isinstance(messages, list):
            self.messages.extend(messages)
        elif isinstance(messages, str):
            self.messages.append(messages)

    def set_result_data(self, data):
        self.result_data = data

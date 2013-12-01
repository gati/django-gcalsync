
class Register(object):
    def __init__(self):
        self.consumers = {}
    
    def register(self, calendar_id, transformers):
        if not calendar_id in self.consumers:
            self.consumers[calendar_id] = transformers
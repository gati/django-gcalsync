import rfc3339

class BaseTransformer(object):
    model = None

    def __init__(self):
        if not self.model:
           raise NotImplementedError("model must be specified") 

    def transform(self):
        raise NotImplementedError("Subclasses must implement transform method")

    def parse_datetime(self, rfc_string):
        return rfc3339.parse_datetime(rfc_string.replace(' ',''))

    def validate(self, event_data):
        if not 'dateTime' in event_data['start']:
            return False

        if not 'dateTime' in event_data['end']:
            return False

        if not 'summary' in event_data:
            return False

        return True
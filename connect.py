import httplib2
from oauth2client.file import Storage

from django.conf import settings

from apiclient.discovery import build

class Connection(object):
    service = None

    def get_service(self):
        if self.service:
            return self.service

        else:
            storage = Storage(settings.GCALSYNC_CREDENTIALS)

            credentials = storage.get()

            http = httplib2.Http()
            http = credentials.authorize(http)

            self.service = build(serviceName='calendar', version='v3', http=http,
                 developerKey=settings.GCALSYNC_APIKEY)

            return self.service
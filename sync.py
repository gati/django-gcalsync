import datetime
import rfc3339

from django.conf import settings

from gcalsync.models import SyncedCalendar, SyncedEvent
from gcalsync.push import async_push_to_gcal
from gcalsync.connect import Connection

class Retriever(object):
    def get_event_list(self, connection=None, calendar_id=None, 
        processor=None, last_retrieved=None, post_retrieval=None):
        
        page_token = None
        if last_retrieved:
            updated_min = rfc3339.datetimetostr(last_retrieved)
        else:
            updated_min = None

        while True:
            events = connection.get_service().events().list(
                calendarId=calendar_id, 
                pageToken=page_token,
                updatedMin=updated_min).execute()

            if events['items']:
                for event in events['items']:
                    processor(event)

            page_token = events.get('nextPageToken')
            if not page_token:
                post_retrieval()
                break


class Synchronizer(object):
    def __init__(self, **kwargs):
        self.calendar_id = kwargs['calendar_id']
        self.transformer = kwargs['transformer']
        self.synced_calendar = self.setup_synced_calendar()

    def setup_synced_calendar(self):
        synced_calendar, created = SyncedCalendar.objects.get_or_create(
            calendar_id=self.calendar_id)

        return synced_calendar

    def sync(self):
        Retriever().get_event_list(connection=Connection(), 
            calendar_id=self.calendar_id, 
            processor=self.process,
            post_retrieval=self.post_retrieval)

    def post_retrieval(self):
        self.synced_calendar.last_synced = datetime.datetime.now()
        self.synced_calendar.save()

    def get_model_data(self, event_data):
        return self.transformer.transform(event_data)

    def extract_gcal_data(self, model_data):
        gcal_event_id = model_data.pop('event_id', None)
        gcal_event_url = model_data.pop('url', None)

        return gcal_event_id, gcal_event_url

    def create_synced_event(self, gcal_event_id, model_data):
        try:
            synced_event = SyncedEvent.objects.get(gcal_event_id=gcal_event_id)
            event_model = synced_event.content_object

            for key,val in model_data.iteritems():
                setattr(event_model, key, val)

            event_model.save()

        except SyncedEvent.DoesNotExist:
            synced_event = SyncedEvent(gcal_event_id=gcal_event_id,
                origin='google')
            event_model = self.transformer.model.objects.create(**model_data)
            synced_event.content_object = event_model
            synced_event.synced_calendar = self.synced_calendar
            synced_event.save()

        return synced_event           

    def process(self, event_data):
        model_data = self.get_model_data(event_data)

        if not model_data:
            return False

        gcal_event_id, gcal_event_url = self.extract_gcal_data(model_data)

        if not gcal_event_id:
            return False

        synced_event = self.create_synced_event(gcal_event_id, model_data)

        synced_event.gcal_event_url = gcal_event_url
        synced_event.save()


def push_to_gcal(sender, instance, **kwargs):
    async_push_to_gcal.delay(instance)

from datetime import datetime, timedelta
import rfc3339

from django.test import TestCase
from django.db import models, connection
from django.utils import simplejson

from gcalsync.transformation import BaseTransformer
from gcalsync.sync import Synchronizer
from gcalsync.push import Pusher
from gcalsync.connect import Connection

sample_event_data = """
{
    "end": {
        "dateTime": "2013-05-30T16: 00: 00-05: 00"
    },
    "htmlLink": "https: //www.google.com/calendar/event?eid=MG5obzNjM2M4NGthYnBwMm90MDdwOGsxZ3Mgam9uYXRob25tb3JnYW5AbQ",
    "summary": "Stuff to do",
    "start": {
        "dateTime": "2013-05-30T15: 00: 00-05: 00"
    },
    "id": "0nho3c3c84kabpp2ot07p8k1gs"
}
"""

sample_event_data = simplejson.loads(sample_event_data)

class TestEvent(models.Model):
    title = models.CharField(max_length=100)

class TestPushEvent(models.Model):
    title = models.CharField(max_length=100)
    start_date  = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    start_time = models.TimeField(blank=True,null=True)
    end_time = models.TimeField(blank=True,null=True)

    def to_gcal(self):
        start_datetime = datetime.combine(self.start_date, self.start_time)
        end_datetime = datetime.combine(self.end_date, self.end_time)
        
        return {
            "start": {
                "dateTime": start_datetime
            },
            "end": {
                "dateTime": end_datetime
            },
            "summary": self.title,
            "calendarId": "primary" 
        }

CREATE_PUSH_TABLE = """
CREATE TABLE gcalsync_testpushevent(id INTEGER NOT NULL, 
    start_date TEXT, start_time TEXT, end_date TEXT, end_time TEXT, 
    title VARCHAR(100), PRIMARY KEY(id))
"""

CREATE_TABLE = """
CREATE TABLE gcalsync_testevent(id INTEGER NOT NULL,  
    title VARCHAR(100), PRIMARY KEY(id))
"""


class TestTransformer(BaseTransformer):
    model = TestEvent

    def transform(self, event_data):
        if not self.validate(event_data):
            return False

        start_datetime = self.parse_datetime(event_data['start']['dateTime'])
        end_datetime = self.parse_datetime(event_data['end']['dateTime'])

        return {
            'title': event_data['summary'],
            'url': event_data['htmlLink'],
            'event_id': event_data['id']
        }

class SynchronizerTest(TestCase):
    def setUp(self):
        super(SynchronizerTest, self).setUp()

        connection.cursor().execute(CREATE_TABLE)

        self.synchronizer = Synchronizer(calendar_id='primary', 
            transformer=TestTransformer())

    def tearDown(self):
        connection.cursor().execute("DROP TABLE gcalsync_testevent")

    def test_transform(self):
        model_data = self.synchronizer.get_model_data(sample_event_data)
        self.assertEqual(model_data['title'], sample_event_data['summary'])

    def test_extract_gcal_data(self):
        model_data = self.synchronizer.get_model_data(sample_event_data)
        gcal_event_id, gcal_event_url = self.synchronizer.extract_gcal_data(model_data)
        self.assertEqual(gcal_event_id, sample_event_data['id'])
        self.assertEqual(gcal_event_url, sample_event_data['htmlLink'])

    def test_create_synced_event(self):
        model_data = self.synchronizer.get_model_data(sample_event_data)
        gcal_event_id, gcal_event_url = self.synchronizer.extract_gcal_data(model_data)
        synced_event = self.synchronizer.create_synced_event(gcal_event_id, model_data)

        self.assertEqual(synced_event.gcal_event_id, gcal_event_id)
        self.assertEqual(synced_event.content_object.title, sample_event_data['summary'])


class PusherTest(TestCase):
    def setUp(self):
        super(PusherTest, self).setUp()

        connection.cursor().execute(CREATE_PUSH_TABLE)

        now = datetime.now()
        tomorrow = now + timedelta(days=1)

        self.test_event = TestPushEvent(
            start_date=now.date(),
            start_time=now.time(),
            title='Test Event',
            end_date=tomorrow.date(),
            end_time=tomorrow.time())

        self.test_event.save()

        self.pusher = Pusher(self.test_event)

    def tearDown(self):
        connection.cursor().execute("DROP TABLE gcalsync_testpushevent")
        service = Connection().get_service()
        service.events().delete(calendarId='primary', eventId=self.created_event['id']).execute()

    def test_create_event(self):
        self.created_event = self.pusher.create_or_update()




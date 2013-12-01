from sync import Synchronizer

from celery.task import PeriodicTask
from celery.registry import tasks
from datetime import timedelta, datetime

_tasks = []

def run(calender_id, transformer):
    def func(self, **kwargs):
        synchronizer = Synchronizer(calendar_id=calender_id, 
            transformer=transformer)

        synchronizer.sync()

    return func


class TaskManager(object):
    def create_task(self, calendar_id, transformer):
        class_name = "CeleryTask_%s_%s" %(calendar_id, type(transformer).__name__)
        return type(class_name, (PeriodicTask,), {
                "run_every": timedelta(seconds=120),
                "run": run(calendar_id, transformer)
            })
        

    def setup_tasks(self, consumer_dict):
        for calendar_id, transformers in consumer_dict.iteritems():
            for Transformer in transformers:
                _tasks.append(self.create_task(calendar_id, Transformer()))

        for Task in _tasks:
            tasks.register(Task)
from registry import Register
from discovery import ConsumerManager
from tasks import TaskManager

_consumer_manager = ConsumerManager()
_task_manager = TaskManager()
_register = Register()

def register(calendar_id, transformers):
    _register.register(calendar_id, transformers)

_consumer_manager.autodiscover()
_task_manager.setup_tasks(_register.consumers)
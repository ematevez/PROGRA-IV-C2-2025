from celery.decorators import task
from celery.utils.log import get_task_logger

@task(name="notify_participant")
def notify_participant(chat_id, msg=None):
    pass
    # send email
    # create notification

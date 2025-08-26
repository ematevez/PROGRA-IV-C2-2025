from celery.decorators import task
from celery.utils.log import get_task_logger
from supplier import models as SupplierModel

@task(name="order_placed_notify_supplier")
def order_placed_notify_supplier(order_id, msg=None):
    pass
    # highlight products ordered for
    # send email
    # create notification

@task(name="notify_suppleir_form_buyer")
def notify_suppleir_form_buyer(order_id, msg=None):
    pass
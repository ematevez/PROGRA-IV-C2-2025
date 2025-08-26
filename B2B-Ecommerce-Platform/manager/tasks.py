from typing import List
from celery.decorators import task
from celery.utils.log import get_task_logger

from manager import models as ManagerModels

from django.utils.translation import get_language
from googletrans import Translator

translator = Translator()
from django.conf import settings

from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from django.apps import apps

@task(name="make_manager_model_translations")
def make_manager_model_translations(fields, instance_id, modal_name, app_name="manager"):

    modal = None
    for model in apps.get_app_config(app_name).get_models():
        if model.__name__ == modal_name:
            modal = model
            break

    if modal_name == "Discussion":
        instance = modal.admin_list.filter(id=instance_id).first()
    else:
        instance = modal.objects.filter(id=instance_id).first()
    
    make_translations(fields, instance, modal)


def make_translations(fields, instance, modal):
    for field in fields:
        for language in settings.LANGUAGES:
            try:
                if language[0] == get_language():
                    # already set
                    continue
                result = translator.translate(
                    getattr(instance, field), dest=language[0]
                )
                for model_field in modal._meta.get_fields():
                    if not model_field.name in f"{field}_{language[0]}":
                        continue

                    if model_field.name == f"{field}_{language[0]}":
                        setattr(instance, model_field.name, result.text)
                        instance.save()
            except Exception as Err:
                print("Error On: ", instance)
                setattr(instance, f"{field}_{language[0]}", getattr(instance, field))
                instance.save()


@task(name="send_email")
def send_mail(subject: str, content : str, _to: List[str] = [], _reply_to: List[str] = [], _from=settings.DEFAULT_FROM_EMAIL, image_url=None):

    email_body = render_to_string(
        "email_message.html",
        {
            "content": "{}".format(content),
            "image_url": None
        },
    )
    email = EmailMessage(
        subject = subject,
        body = email_body,
        from_email = _from,
        to = _to,
        reply_to = _reply_to
    )
    email.content_subtype = 'html'
    if image_url:
        email.attach_file('image_url')

    email.send(fail_silently=False)

    # save email
    ManagerModels.SentEmail.objects.create(
        recipient = ", ".join(_to),
        subject = subject,
        sending_email = _from,
        content = content,
        reply_to = ", ".join(_reply_to) if _reply_to else None
    )
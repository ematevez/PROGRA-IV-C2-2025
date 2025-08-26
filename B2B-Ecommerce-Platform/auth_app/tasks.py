from celery.decorators import task
from celery.utils.log import get_task_logger
from auth_app.email import send_account_activation_email

from auth_app import models as AuthModels

from payment.management.commands.utils.braintree import braintree_config

from django.utils.translation import get_language
from googletrans import Translator

translator = Translator()
from django.conf import settings

# this output messages to the celery log
logger = get_task_logger(__name__)


@task(name="send_account_activation_email_task")
def send_account_activation_email_task(name, email, subject, description):
    logger.info("Sent Activation email")
    return send_account_activation_email(name, email, subject, description)


@task(name="create_braintree_customer")
def create_braintree_customer(profile_id):
    logger.info("Creating braintree customer")
    try:
        profile = AuthModels.ClientProfile.objects.filter(pk=profile_id).first()
        result = braintree_config.get_braintree_gateway().customer.create(
            {
                "first_name": profile.user.first_name,
                "last_name": profile.user.last_name,
                "company": profile.business_name,
                "email": profile.user.email,
                "phone": profile.mobile_user,
            }
        )

        if result.is_success:
            profile.customer_id = result.customer.id
            profile.save
            logger.info("Braintree Customer Created Successful")
        else:
            logger.info("Braintree Customer Creation Failed. Error {}".format(result))
    except Exception as e:
        logger.info("Braintree Customer Creation Failed. Error {}".format(e))


@task(name="make_business_translations")
def make_business_translations(fields, instance_id):
    modal = AuthModels.ClientProfile
    instance = modal.objects.filter(id=instance_id).first()
    make_translations(fields, instance, modal)


@task(name="make_user_translations")
def make_user_translations(fields, instance_id):
    modal = AuthModels.User
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
            except:
                setattr(instance, f"{field}_{language[0]}", getattr(instance, field))
                instance.save()

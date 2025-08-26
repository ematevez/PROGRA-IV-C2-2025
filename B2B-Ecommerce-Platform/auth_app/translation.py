from modeltranslation.translator import register, TranslationOptions
from auth_app import models


@register(models.User)
class UserTranslationOptions(TranslationOptions):
    fields = ("first_name", "last_name")


@register(models.ClientProfile)
class ClientProfileTranslationOptions(TranslationOptions):
    fields = (
        "business_name",
        "business_description",
        "country",
        "country_code",
        "city",
        "mobile_user",
    )

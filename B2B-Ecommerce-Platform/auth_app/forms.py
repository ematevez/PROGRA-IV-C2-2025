from django import forms
from allauth.socialaccount.forms import SignupForm

from django.forms import ModelForm

from auth_app import models as AuthModels

class CustomSocialSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        CHOICES = [("SUPPLIER", "Supplier"), ("BUYER", "Buyer")]
        super().__init__(*args, **kwargs)
        self.fields['account_type'] = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

    def save(self, request):
        user = super(CustomSocialSignupForm, self).save(request)
        user.account_type = self.cleaned_data["account_type"]
        user.active = True
        user.is_email_activated = True
        user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        # Add your custom validation here
        return cleaned_data

class UserProfileFormManager(ModelForm):
    class Meta:
        model = AuthModels.ClientProfile
        fields = "__all__"


class UserProfileUpdateFormManager(ModelForm):
    class Meta:
        model = AuthModels.ClientProfile
        exclude = ("user", "slug")


class UserFormManager(ModelForm):
    class Meta:
        model = AuthModels.User
        fields = "__all__"


class UserUpdateFormManager(ModelForm):
    class Meta:
        model = AuthModels.User
        fields = ("email", "first_name", "last_name", "username")

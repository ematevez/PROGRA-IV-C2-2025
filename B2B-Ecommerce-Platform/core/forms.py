from django import forms
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        CHOICES = [("SUPPLIER", "Supplier"), ("BUYER", "Buyer")]
        self.fields['account_type'] = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.account_type = self.cleaned_data["account_type"]
        user.active = True
        user.is_email_activated = True
        user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        # Add your custom validation here
        return cleaned_data

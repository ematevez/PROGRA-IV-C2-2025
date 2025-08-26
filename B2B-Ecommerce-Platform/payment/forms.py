"""
Add a simple form, which includes the hidden payment nonce field.
You might want to add other fields like an address, quantity or
an amount.
"""
from django import forms
from django.utils.translation import gettext_lazy as _


class CheckoutForm(forms.Form):
    payment_method_nonce = forms.CharField(
        max_length=1000,
        widget=forms.widgets.HiddenInput,
        required=False,  # In the end it's a required field, but I wanted to provide a custom exception message
    )

    def clean(self):
        self.cleaned_data = super(CheckoutForm, self).clean()
        # Braintree nonce is missing
        if not self.cleaned_data.get("payment_method_nonce"):
            raise forms.ValidationError(
                _("We couldn't verify your payment. Please try again.")
            )
        return self.cleaned_data

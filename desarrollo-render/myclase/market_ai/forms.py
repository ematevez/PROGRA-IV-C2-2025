from django import forms
from market.models import Product

class PriceSuggestForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)
    marca = forms.CharField(max_length=100, required=False)
    current_price = forms.DecimalField(max_digits=12, decimal_places=2, required=False)

class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={"rows":2}), label="Tu mensaje")

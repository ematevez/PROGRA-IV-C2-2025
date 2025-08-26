from django import forms

from manager import models as ManagerModels

class ServiceFormManager(forms.ModelForm):
    class Meta:
        model = ManagerModels.Service
        fields = ["name", "description"]

class ShowroomFormManager(forms.ModelForm):
    class Meta:
        model = ManagerModels.Showroom
        fields = ["name", "location", "image"]

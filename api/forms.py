from django import forms
from .models import Shipment


class ShipmentModelForm(forms.ModelForm):
    req_body = forms.CharField(widget=forms.Textarea, required=False)
    delivery_message = forms.CharField(widget=forms.Textarea, required=False)
    delivery_notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Shipment
        exclude = ('id',)

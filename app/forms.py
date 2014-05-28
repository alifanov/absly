from django.forms import ModelForm
from app.models import SummaryItem

class SummaryItemForm(ModelForm):
    class Meta:
        model = SummaryItem
        fields = ['text']
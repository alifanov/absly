from django.forms import ModelForm
from app.models import SummaryItem, GAFunnelConfig

class FunnelConfgiForm(ModelForm):
    class Meta:
        model = GAFunnelConfig
        exclude=('user',)

class SummaryItemForm(ModelForm):
    class Meta:
        model = SummaryItem
        fields = ['text']
from django.forms import ModelForm
from app.models import *

class FunnelConfgiForm(ModelForm):
    class Meta:
        model = GAFunnelConfig

class SummaryItemForm(ModelForm):
    class Meta:
        model = SummaryItem

class SummaryTextBlockForm(ModelForm):
    class Meta:
        model = SummaryTextBlock
        exclude = ('item',)

class SummaryImageBlockForm(ModelForm):
    class Meta:
        model = SummaryImageBlock

class SummaryLinkBlockForm(ModelForm):
    class Meta:
        model = SummaryLinkBlock


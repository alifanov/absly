from django.forms import ModelForm, HiddenInput
from app.models import *

class FunnelConfgiForm(ModelForm):
    class Meta:
        model = GAFunnelConfig

class SummaryItemForm(ModelForm):
    class Meta:
        model = SummaryItem

class SummaryTextBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryTextBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryTextBlock

class SummaryImageBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryImageBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryImageBlock

class SummaryLinkBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryLinkBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryLinkBlock


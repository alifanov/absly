from django.forms import ModelForm, HiddenInput, TextInput, ModelChoiceField
from app.models import *

class CanvasLogForm(ModelForm):
    class Meta:
        model = CanvasLogEntry
        exclude = ('created',)

class CanvasElementForm(ModelForm):
    def add_params(self, block):
        for p in block.params.all():
            self.fields['params'] = []
            self.fields['params'].append(ModelChoiceField(queryset=p.values.all()))

    class Meta:
        model = CanvasBlockItem
        fields = ('name', 'segment', 'block')

class FunnelConfgiForm(ModelForm):
    class Meta:
        model = GAFunnelConfig
        exclude=('start_date', 'end_date', 'user')

class FunnelDateForm(ModelForm):
    class Meta:
        model = GAFunnelConfig
        fields = ('date_range',)

class FunnelDataForm(ModelForm):
    class Meta:
        model = GAFunnelConfig
        fields = ('activation_value', 'retention_value', 'referral_value', 'revenue_value')

class SummaryItemForm(ModelForm):
    class Meta:
        model = SummaryItem

class SummaryTextBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryTextBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryTextBlock
        exclude=('user',)

class SummaryImageBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryImageBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryImageBlock
        exclude=('user',)

class SummaryLinkBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryLinkBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()
        self.fields['link'].widget = TextInput(attrs={
            'placeholder': 'Insert link'
        })
        self.fields['title'].widget = TextInput(attrs={
            'placeholder': 'Insert title'
        })

    class Meta:
        model = SummaryLinkBlock
        exclude=('user',)

class SummaryLinkedInBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryLinkedInBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()
        self.fields['link'].widget = TextInput(attrs={
            'placeholder': 'Insert link'
        })

    class Meta:
        model = SummaryLinkedInBlock
        exclude=['title', 'avatar', 'name', 'desc', 'user']

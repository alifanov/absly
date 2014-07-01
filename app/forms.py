from django.forms import ModelForm, HiddenInput, TextInput
from app.models import *

class FunnelConfgiForm(ModelForm):
    class Meta:
        model = GAFunnelConfig
        exclude=('start_date', 'end_date', 'user')

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

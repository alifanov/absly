from django.forms import ModelForm, HiddenInput, TextInput, ModelChoiceField
from app.models import *

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ('user', 'customers')

class CanvasLogForm(ModelForm):
    class Meta:
        model = CanvasLogEntry
        exclude = ('created',)

class CanvasElementForm(ModelForm):
    def add_params(self, block, element=None):
        for i, p in enumerate(block.params.all()):
            initial = None
            if element:
                initial = element.params_values.filter(parameter=p)
                if initial.count(): initial = initial[0]
            self.fields['param_{}'.format(i)] = ModelChoiceField(queryset=p.values.all().distinct(), label=p.name, initial=initial)

    def __init__(self, *args, **kwargs):
        super(CanvasElementForm, self).__init__(*args, **kwargs)
        self.fields['segment'].queryset = CanvasBlockItem.objects.filter(block__name=u'Customer Segments')

    class Meta:
        model = CanvasBlockItem
        fields = ('name', 'segment', 'block', 'user')

class FunnelConfgiForm(ModelForm):
    class Meta:
        model = GAFunnelConfig
        exclude = ['start_date', 'end_date', 'user', 'date_range']

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

class SummaryAngelListBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryAngelListBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()
        self.fields['link'].widget = TextInput(attrs={
            'placeholder': 'Insert link'
        })

    class Meta:
        model = SummaryAngelListBlock
        exclude=['title', 'photo', 'name', 'desc', 'user', 'startup_id']

class SummaryCrunchBaseBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryCrunchBaseBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()
        self.fields['link'].widget = TextInput(attrs={
            'placeholder': 'Insert link'
        })

    class Meta:
        model = SummaryCrunchBaseBlock
        exclude=['title', 'photo', 'name', 'desc', 'user']

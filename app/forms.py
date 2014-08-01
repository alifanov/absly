from django.forms import ModelForm, HiddenInput, TextInput, ModelChoiceField
from django import forms
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
        exclude = ['user', 'date_range', 'activation_value', 'retention_value', 'referral_value', 'revenue_value']

class FunnelDateForm(ModelForm):
    class Meta:
        model = GAFunnelConfig
        fields = ('date_range',)

# class FunnelDataForm(ModelForm):
#     class Meta:
#         model = GAFunnelConfig
#         fields = ('activation_value', 'retention_value', 'referral_value', 'revenue_value')

class GALogDataForm(ModelForm):
    class Meta:
        model = GALogData
        exclude = ['start_date', 'end_date', 'user']

class SummaryItemForm(ModelForm):
    class Meta:
        model = SummaryItem

class SummaryValuationBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryValuationBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryValuationBlock
        exclude=('user',)

class SummaryMarketSizeBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryMarketSizeBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryMarketBlock
        exclude=('user',)

class SummaryInvestmentRequestBlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SummaryInvestmentRequestBlockForm, self).__init__(*args, **kwargs)
        self.fields['item'].widget = HiddenInput()

    class Meta:
        model = SummaryInvestmentRequestBlock
        exclude=('user',)

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

class SnapshotForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SnapshotForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget = TextInput()

    class Meta:
        model = Snapshot
        exclude = ['user',]

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


attrs_dict = {'class': 'required'}

class RegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=256)),
        label=_("Email")
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password")
    )
    def clean_email(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        email = self.cleaned_data['email'].strip()
        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return email.lower()
        raise forms.ValidationError(
            _('A user with that email already exists.'))

    def clean(self):
        """
        Verifiy that the values entered into the two password fields match.

        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.

        """
        data = self.cleaned_data
        if not 'email' in data:
            return data
        if not 'password' in data:
            return data
        return self.cleaned_data


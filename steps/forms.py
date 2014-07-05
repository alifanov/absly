from django import forms
from steps.models import Step

class StepForm(forms.ModelForm):

    # def clean_deadline(self):
    #     date = self.cleaned_data.get('deadline')
    #     return date + ' 00:00'
    #
    class Meta:
        model = Step
        exclude = ('user',)
from django import forms
from steps.models import Step

class StepForm(forms.ModelForm):

    class Meta:
        model = Step
        exclude = ('done_log', 'user','target_metrics_current')

class StepEditForm(forms.ModelForm):
    class Meta:
        model = Step
        exclude = ('user',)
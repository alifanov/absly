from django import forms
from steps.models import Step

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
from django import forms
from steps.models import Step
from bootstrap3_datetime.widgets import DateTimePicker

class StepForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StepForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget = DateTimePicker({
            "format": "YYYY-MM-DD HH:mm",
            "pickSeconds": False
        })

    class Meta:
        model = Step
        exclude = ('user',)
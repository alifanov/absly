from django import forms
from talk.models import *

class SystemCommentForm(forms.ModelForm):
    class Meta:
        model = SystemComment
        fields = ('text',)
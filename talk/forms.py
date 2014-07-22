from django import forms
from talk.models import *

class SystemCommentForm(forms.ModelForm):
    class Meta:
        model = SystemComment
        fields = ('text',)

class PostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
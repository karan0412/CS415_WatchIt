from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'feedback', 'file']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'})
        }

from django import forms
from .models import CareerApplication, Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'feedback', 'file']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'})
        }


class CareerApplicationForm(forms.ModelForm):
    class Meta:
        model = CareerApplication
        fields = ['name', 'cv', 'cover_letter']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'cv': forms.FileInput(attrs={'class': 'form-control-file'}),
            'cover_letter': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

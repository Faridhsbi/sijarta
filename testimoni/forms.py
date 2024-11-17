from django import forms
from .models import Testimoni

class TestimoniForm(forms.ModelForm):
    class Meta:
        model = Testimoni
        fields = ['rating', 'komentar']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'komentar': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

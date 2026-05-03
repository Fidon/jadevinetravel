from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.HiddenInput(),
        error_messages={
            'min_value': _('Rating must be at least 1.'),
            'max_value': _('Rating cannot exceed 10.'),
            'required': _('Please select a rating.'),
        }
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'jd-input',
            'rows': 4,
            'placeholder': _('Tell us about your experience (optional)…'),
        }),
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
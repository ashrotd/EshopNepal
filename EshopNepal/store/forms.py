from django import forms
from django.forms import fields
from store.models import ReviewSystem

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewSystem
        fields = ['subject','review','rating']
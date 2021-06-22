from django import forms
from django.db.models import fields
from django.forms.widgets import PasswordInput
from .models import Account

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=PasswordInput(attrs={
        'placeholder' : 'Create Password',
        'class':'form-control'
    }))
    confirm_password = forms.CharField(widget=PasswordInput(attrs={
        'placeholder':'Confirm Password',
        'class':'form-control'
    }))
    class Meta:
        model = Account
        fields = ['first_name','last_name','email','phone_number','password']

    def __init__(self,*args, **kwargs):
        super(RegisterForm,self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Last Name'
        self.fields['email'].widget.attrs['placeholder']='Email'
        self.fields['phone_number'].widget.attrs['placeholder']='Phone Number'
        for i in self.fields:
            self.fields[i].widget.attrs['class']='form-control'

    def clean(self):
        cleaned_data = super(RegisterForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Password Does not match'
            )
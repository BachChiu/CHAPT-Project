from django import forms
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.Form):
    userID = forms.CharField()
    fname = forms.CharField(max_length=30, required=True)
    lname = forms.CharField(max_length=30, required=True)
    userPass = forms.CharField(widget=forms.PasswordInput)
    userPass2 = forms.CharField(widget=forms.PasswordInput)
    companyID = forms.CharField(required=False)
    role = forms.CharField(required=False)

    def clean_userPass2(self):
        password1 = self.cleaned_data.get("userPass")
        password2 = self.cleaned_data.get("userPass2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        return password2  # Always return the cleaned value

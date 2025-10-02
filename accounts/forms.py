from django import forms
from django.core.exceptions import ValidationError
from .models import Student
from .validators import validate_not_disposable_email


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = ["username", "email", "phone"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if Student.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with that email already exists.")
        # Block disposable and dummy emails
        validate_not_disposable_email(email)
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match")
        if p1 and len(p1) < 8:
            self.add_error("password1", "Password must be at least 8 characters long")
        return cleaned

    def save(self, commit: bool = True) -> Student:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.CharField(label="Email or Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["username", "phone", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


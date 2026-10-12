from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from accounts.models import PersianUsernameValidator, Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="نام کاربری")
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="نام کاربری",
        max_length=150,
        validators=[PersianUsernameValidator()],
        error_messages={"unique": "این نام کاربری قبلاً ثبت شده است."},
    )
    first_name = forms.CharField(label="نام", max_length=150)
    password1 = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    password2 = forms.CharField(label="تکرار رمز عبور", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "first_name", "email")
        labels = {"username": "نام کاربری", "first_name": "نام", "email": "ایمیل"}


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="نام", max_length=150)
    last_name = forms.CharField(label="نام خانوادگی", max_length=150, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {"first_name": "نام", "last_name": "نام خانوادگی", "email": "ایمیل"}


class AddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone", "address", "postal_code")
        labels = {
            "phone": "شماره تماس",
            "address": "نشانی",
            "postal_code": "کد پستی",
        }
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if phone and (not phone.isdigit() or len(phone) != 11):
            raise forms.ValidationError("شماره تماس باید ۱۱ رقم عدد باشد.")
        return phone

    def clean_postal_code(self):
        code = self.cleaned_data["postal_code"]
        if code and (not code.isdigit() or len(code) != 10):
            raise forms.ValidationError("کد پستی باید ۱۰ رقم عدد باشد.")
        return code

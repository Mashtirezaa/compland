from django import forms

from orders.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("full_name", "phone", "address", "postal_code", "note")
        labels = {
            "full_name": "نام و نام خانوادگی",
            "phone": "شماره تماس",
            "address": "نشانی کامل",
            "postal_code": "کد پستی",
            "note": "توضیحات سفارش (اختیاری)",
        }
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "note": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not phone.isdigit() or len(phone) != 11:
            raise forms.ValidationError("شماره تماس باید ۱۱ رقم عدد باشد.")
        return phone

    def clean_postal_code(self):
        code = self.cleaned_data["postal_code"]
        if not code.isdigit() or len(code) != 10:
            raise forms.ValidationError("کد پستی باید ۱۰ رقم عدد باشد.")
        return code

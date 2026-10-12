from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class PersianUsernameValidator(RegexValidator):
    regex = r"^[\w.@+\-\u200c\u200d ]+$"
    message = "نام کاربری می‌تواند حروف فارسی یا انگلیسی، عدد، نقطه، خط تیره و نیم‌فاصله باشد."
    flags = 0


_username = User._meta.get_field("username")
_username.validators = [PersianUsernameValidator()] + [v for v in _username.validators if not hasattr(v, "regex")]
_username.help_text = "حروف فارسی و انگلیسی، عدد و نیم‌فاصله مجاز است."


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def __str__(self):
        return self.user.username

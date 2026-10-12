from django.conf import settings
from django.db import models


class UserCart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_cart")
    items = models.JSONField(default=dict)

    class Meta:
        verbose_name = "سبد ذخیره شده"
        verbose_name_plural = "سبدهای ذخیره شده"

    def __str__(self):
        return str(self.user)

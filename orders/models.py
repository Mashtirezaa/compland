from django.contrib.auth.models import User
from django.db import models

from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("processing", "در حال پردازش"),
        ("sent", "ارسال شده"),
        ("delivered", "تحویل شده"),
        ("canceled", "لغو شده"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    postal_code = models.CharField(max_length=15)
    note = models.TextField(blank=True)
    total = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"سفارش {self.id} - {self.full_name}"

    @property
    def can_cancel(self):
        return self.status in ("pending", "processing")

    @property
    def can_edit(self):
        return self.can_cancel


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"

    def __str__(self):
        return self.name

    @property
    def total(self):
        return self.price * self.quantity

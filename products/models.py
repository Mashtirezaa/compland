from django.conf import settings
from django.db import models
from django.urls import reverse

from products.images import media_url


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    price = models.PositiveIntegerField()
    discount = models.PositiveSmallIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    sales = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    reviews = models.PositiveIntegerField(default=0)
    image = models.CharField(max_length=120, blank=True)
    gallery = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product", args=[self.slug])

    @property
    def final_price(self):
        return self.price - self.price * self.discount // 100

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def image_url(self):
        return media_url("products", self.image) or media_url("products", self.slug)

    @property
    def gallery_urls(self):
        urls = [self.image_url] if self.image_url else []
        for name in self.gallery.split(","):
            url = media_url("products", name.strip())
            if url and url not in urls:
                urls.append(url)
        return urls

    @property
    def rating_percent(self):
        return int(self.rating * 20)


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
    key = models.CharField(max_length=60)
    value = models.CharField(max_length=120)

    class Meta:
        verbose_name = "مشخصه فنی"
        verbose_name_plural = "مشخصات فنی"
        unique_together = ("product", "key")

    def __str__(self):
        return f"{self.key}: {self.value}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    is_buyer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.username

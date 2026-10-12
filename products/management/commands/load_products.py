import json
from pathlib import Path

from django.core.management.base import BaseCommand

from products.models import Brand, Category, Product, ProductSpec

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "products.json"


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

        for item in data["categories"]:
            Category.objects.update_or_create(
                slug=item["slug"], defaults={"name": item["name"], "icon": item.get("icon", "")})

        for item in data["products"]:
            brand, _ = Brand.objects.update_or_create(
                slug=item["brand"].lower(), defaults={"name": item["brand"]})
            product, _ = Product.objects.update_or_create(slug=item["slug"], defaults={
                "category": Category.objects.get(slug=item["category"]),
                "brand": brand,
                "name": item["name"],
                "price": item["price"],
                "discount": item.get("discount", 0),
                "stock": item.get("stock", 0),
                "sales": item.get("sales", 0),
                "rating": item.get("rating", 0),
                "reviews": item.get("reviews", 0),
                "image": item.get("image", ""),
                "gallery": item.get("gallery", ""),
                "description": item.get("description", ""),
            })
            product.specs.all().delete()
            ProductSpec.objects.bulk_create(
                [ProductSpec(product=product, key=key, value=value) for key, value in item["specs"].items()])

from products.models import Category


def menu(request):
    return {
        "categories": Category.objects.all(),
        "cart_count": sum(request.session.get("cart", {}).values()),
        "compare_count": len(request.session.get("compare", [])),
    }

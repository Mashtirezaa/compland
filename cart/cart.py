from cart.models import UserCart
from products.models import Product


def get_cart(request):
    raw = request.session.get("cart", {})
    items = []
    total = 0
    for product in Product.objects.filter(id__in=raw.keys()):
        qty = raw.get(str(product.id), 0)
        if qty < 1:
            continue
        line_total = product.final_price * qty
        items.append({"product": product, "qty": qty, "total": line_total})
        total += line_total
    return {"items": items, "total": total}


def save_qty(request, product, qty):
    cart = request.session.get("cart", {})
    if qty < 1:
        cart.pop(str(product.id), None)
    else:
        cart[str(product.id)] = min(qty, product.stock)
    request.session["cart"] = cart
    persist_cart(request)


def persist_cart(request):
    if not request.user.is_authenticated:
        return
    saved, _ = UserCart.objects.get_or_create(user=request.user)
    saved.items = request.session.get("cart", {})
    saved.save(update_fields=["items"])


def restore_cart(request):
    if not request.user.is_authenticated:
        return
    saved = UserCart.objects.filter(user=request.user).first()
    stored = dict(saved.items) if saved else {}
    current = dict(request.session.get("cart") or {})
    merged = stored
    for key, qty in current.items():
        merged[str(key)] = int(merged.get(str(key), 0)) + int(qty or 0)
    clean = {}
    for product in Product.objects.filter(id__in=list(merged.keys())):
        qty = min(int(merged.get(str(product.id), 0)), product.stock)
        if qty > 0:
            clean[str(product.id)] = qty
    request.session["cart"] = clean
    persist_cart(request)


def next_url(request):
    target = request.POST.get("next", "")
    return target if target.startswith("/") and not target.startswith("//") else "/cart/"

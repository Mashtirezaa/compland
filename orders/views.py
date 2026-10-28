from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile
from cart.cart import get_cart, persist_cart
from orders.forms import OrderForm
from orders.models import Order, OrderItem


@login_required
def checkout(request):
    cart = get_cart(request)
    if not cart["items"]:
        messages.warning(request, "سبد خرید شما خالی است.")
        return redirect("cart:detail")

    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    form = OrderForm(request.POST or None, initial={
        "full_name": request.user.get_full_name(),
        "phone": user_profile.phone,
        "address": user_profile.address,
        "postal_code": user_profile.postal_code,
    })
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart["total"]
            order.save()
            for item in cart["items"]:
                OrderItem.objects.create(order=order, product=item["product"], name=item["product"].name,
                                         price=item["product"].final_price, quantity=item["qty"])
                product = item["product"]
                product.stock -= item["qty"]
                product.sales += item["qty"]
                product.save(update_fields=["stock", "sales"])
            request.session["cart"] = {}
            persist_cart(request)
        return redirect("orders:done", id=order.id)

    return render(request, "checkout.html", {"form": form, **cart})


@login_required
def done(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, "done.html", {"order": order})


@login_required
def detail(request, id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), id=id, user=request.user)
    form = None
    if order.can_edit:
        form = OrderForm(request.POST or None, instance=order)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "اطلاعات سفارش به‌روز شد.")
            return redirect("orders:detail", id=order.id)
    return render(request, "order_detail.html", {"order": order, "form": form})


@login_required
@require_POST
def cancel(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    if not order.can_cancel:
        messages.error(request, "این سفارش را نمی‌توان لغو کرد.")
        return redirect("accounts:profile")

    with transaction.atomic():
        for item in order.items.select_related("product"):
            product = item.product
            if not product:
                continue
            product.stock += item.quantity
            product.sales = max(0, product.sales - item.quantity)
            product.save(update_fields=["stock", "sales"])
        order.status = "canceled"
        order.save(update_fields=["status"])
    messages.success(request, f"سفارش شماره {order.number} لغو شد و موجودی کالا برگشت.")
    return redirect("accounts:profile")

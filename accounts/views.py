from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import AddressForm, LoginForm, ProfileForm, RegisterForm
from accounts.models import Profile
from cart.cart import persist_cart, restore_cart


class MyLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        restore_cart(self.request)
        return response


@require_POST
def logout_view(request):
    persist_cart(request)
    logout(request)
    return redirect("/")


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"{user.username} عزیز، خوش آمدید.")
        return redirect(request.POST.get("next") or "/")
    return render(request, "register.html", {"form": form, "next": request.GET.get("next", "")})


@login_required
def profile(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(instance=request.user)
    address_form = AddressForm(instance=user_profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        address_form = AddressForm(request.POST, instance=user_profile)
        if form.is_valid() and address_form.is_valid():
            form.save()
            address_form.save()
            messages.success(request, "اطلاعات حساب ذخیره شد.")
            return redirect("accounts:profile")

    return render(request, "profile.html", {
        "form": form,
        "address_form": address_form,
        "orders": request.user.orders.prefetch_related("items"),
    })

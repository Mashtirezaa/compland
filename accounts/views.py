from secrets import randbelow
from time import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import AddressForm, EmailChangeForm, LoginForm, OtpForm, ProfileForm, RegisterForm
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


def _send_code(email, code):
    send_mail(
        "کد تأیید کامپ‌لند",
        f"کد تأیید شما: {code}\nاین کد پنج دقیقه اعتبار دارد.",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = f"{randbelow(1000000):06d}"
        request.session["otp"] = {
            "username": form.cleaned_data["username"],
            "first_name": form.cleaned_data["first_name"],
            "email": form.cleaned_data["email"],
            "password": make_password(form.cleaned_data["password1"]),
            "code": code,
            "until": time() + 300,
            "next": request.POST.get("next") or "/",
        }
        try:
            _send_code(form.cleaned_data["email"], code)
        except Exception:
            messages.error(request, "ارسال ایمیل ممکن نشد. تنظیمات ایمیل را بررسی کنید.")
            return render(request, "register.html", {"form": form, "next": request.POST.get("next", "")})
        messages.success(request, "کد تأیید به ایمیل شما ارسال شد.")
        return redirect("accounts:verify")
    return render(request, "register.html", {"form": form, "next": request.GET.get("next", "")})


def verify(request):
    pending = request.session.get("otp")
    if not pending:
        return redirect("accounts:register")
    form = OtpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if time() > pending["until"]:
            messages.error(request, "کد منقضی شده است. دوباره ثبت‌نام کنید.")
            request.session.pop("otp", None)
            return redirect("accounts:register")
        if form.cleaned_data["code"] != pending["code"]:
            messages.error(request, "کد تأیید نادرست است.")
        elif User.objects.filter(username=pending["username"]).exists():
            messages.error(request, "این نام کاربری قبلاً ثبت شده است.")
            request.session.pop("otp", None)
            return redirect("accounts:register")
        else:
            user = User(
                username=pending["username"],
                first_name=pending["first_name"],
                email=pending["email"],
                password=pending["password"],
            )
            user.save()
            request.session.pop("otp", None)
            login(request, user)
            messages.success(request, f"{user.username} عزیز، خوش آمدید.")
            return redirect(pending.get("next") or "/")
    return render(request, "verify.html", {"form": form, "email": pending["email"]})


def _new_code(pending, email=None):
    code = f"{randbelow(1000000):06d}"
    pending["code"] = code
    pending["until"] = time() + 300
    if email:
        pending["email"] = email
    return pending, code


@require_POST
def resend_code(request):
    pending = request.session.get("otp")
    if not pending:
        return redirect("accounts:register")
    pending, code = _new_code(pending)
    request.session["otp"] = pending
    try:
        _send_code(pending["email"], code)
        messages.success(request, "کد جدید ارسال شد.")
    except Exception:
        messages.error(request, "ارسال ایمیل ممکن نشد.")
    return redirect("accounts:verify")


def change_email(request):
    pending = request.session.get("otp")
    if not pending:
        return redirect("accounts:register")
    form = EmailChangeForm(request.POST or None, initial={"email": pending["email"]})
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        pending, code = _new_code(pending, email)
        request.session["otp"] = pending
        try:
            _send_code(email, code)
            messages.success(request, "کد تأیید به ایمیل جدید ارسال شد.")
            return redirect("accounts:verify")
        except Exception:
            messages.error(request, "ارسال ایمیل ممکن نشد.")
    return render(request, "change_email.html", {"form": form, "email": pending["email"]})


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

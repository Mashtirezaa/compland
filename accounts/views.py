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

from accounts.forms import (
    AddressForm, EmailChangeForm, ForgotForm, LoginForm, OtpForm,
    ProfileForm, RegisterForm, ResetPasswordForm,
)
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


RESEND_WAIT = 60
_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _wait_left(pending):
    sent = float(pending.get("sent") or 0)
    return max(0, int(RESEND_WAIT - (time() - sent)))


def _wait_msg(left):
    return f"تا ارسال دوباره {str(left).translate(_FA_DIGITS)} ثانیه مانده."


def _send_code(email, code, subject="کد تأیید کامپ‌لند"):
    send_mail(
        subject,
        f"کد شما: {code}\nاین کد پنج دقیقه اعتبار دارد.",
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
            "sent": time(),
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
    return render(request, "verify.html", {"form": form, "email": pending["email"], "wait": _wait_left(pending)})


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
    left = _wait_left(pending)
    if left:
        messages.error(request, _wait_msg(left))
        return redirect("accounts:verify")
    pending, code = _new_code(pending)
    try:
        _send_code(pending["email"], code)
        pending["sent"] = time()
        messages.success(request, "کد جدید ارسال شد.")
    except Exception:
        messages.error(request, "ارسال ایمیل ممکن نشد.")
    request.session["otp"] = pending
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
            pending["sent"] = time()
            request.session["otp"] = pending
            messages.success(request, "کد تأیید به ایمیل جدید ارسال شد.")
            return redirect("accounts:verify")
        except Exception:
            messages.error(request, "ارسال ایمیل ممکن نشد.")
    return render(request, "change_email.html", {"form": form, "email": pending["email"]})


def forgot(request):
    form = ForgotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "این ایمیل ثبت نشده است.")
        else:
            code = f"{randbelow(1000000):06d}"
            request.session["reset"] = {
                "user_id": user.id,
                "email": email,
                "code": code,
                "until": time() + 300,
                "sent": time(),
                "ok": False,
            }
            try:
                _send_code(email, code, "کد بازیابی رمز کامپ‌لند")
                messages.success(request, "کد بازیابی به ایمیل شما ارسال شد.")
                return redirect("accounts:reset_code")
            except Exception:
                messages.error(request, "ارسال ایمیل ممکن نشد. تنظیمات ایمیل را بررسی کنید.")
    return render(request, "forgot.html", {"form": form})


def reset_code(request):
    pending = request.session.get("reset")
    if not pending:
        return redirect("accounts:forgot")
    form = OtpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if time() > pending["until"]:
            messages.error(request, "کد منقضی شده است. دوباره درخواست کنید.")
            request.session.pop("reset", None)
            return redirect("accounts:forgot")
        if form.cleaned_data["code"] != pending["code"]:
            messages.error(request, "کد تأیید نادرست است.")
        else:
            pending["ok"] = True
            request.session["reset"] = pending
            return redirect("accounts:reset_password")
    return render(request, "reset_code.html", {"form": form, "email": pending["email"], "wait": _wait_left(pending)})


@require_POST
def reset_resend(request):
    pending = request.session.get("reset")
    if not pending:
        return redirect("accounts:forgot")
    left = _wait_left(pending)
    if left:
        messages.error(request, _wait_msg(left))
        return redirect("accounts:reset_code")
    code = f"{randbelow(1000000):06d}"
    pending["code"] = code
    pending["until"] = time() + 300
    pending["ok"] = False
    try:
        _send_code(pending["email"], code, "کد بازیابی رمز کامپ‌لند")
        pending["sent"] = time()
        messages.success(request, "کد جدید ارسال شد.")
    except Exception:
        messages.error(request, "ارسال ایمیل ممکن نشد.")
    request.session["reset"] = pending
    return redirect("accounts:reset_code")


def reset_password(request):
    pending = request.session.get("reset")
    if not pending or not pending.get("ok"):
        return redirect("accounts:forgot")
    form = ResetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.filter(id=pending["user_id"]).first()
        if not user:
            request.session.pop("reset", None)
            messages.error(request, "حساب پیدا نشد.")
            return redirect("accounts:forgot")
        user.set_password(form.cleaned_data["password1"])
        user.save()
        request.session.pop("reset", None)
        login(request, user)
        restore_cart(request)
        messages.success(request, "رمز عبور عوض شد.")
        return redirect("accounts:profile")
    return render(request, "reset_password.html", {"form": form})


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

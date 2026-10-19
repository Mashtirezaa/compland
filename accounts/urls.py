from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.MyLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("verify/", views.verify, name="verify"),
    path("verify/resend/", views.resend_code, name="resend"),
    path("verify/email/", views.change_email, name="change_email"),
    path("profile/", views.profile, name="profile"),
]

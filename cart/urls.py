from django.urls import path

from cart import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("add/<int:id>/", views.add_to_cart, name="add"),
    path("update/<int:id>/", views.update_cart, name="update"),
]

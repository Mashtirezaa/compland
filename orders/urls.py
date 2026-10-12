from django.urls import path

from orders import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("done/<int:id>/", views.done, name="done"),
    path("order/<int:id>/", views.detail, name="detail"),
    path("cancel/<int:id>/", views.cancel, name="cancel"),
]

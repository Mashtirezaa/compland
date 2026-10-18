from django.urls import path

from products import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.product_list, name="search"),
    path("category/<slug:slug>/", views.product_list, name="category"),
    path("product/<slug:slug>/", views.product_detail, name="product"),
    path("product/<slug:slug>/review/", views.add_review, name="add_review"),
    path("compare/", views.compare_list, name="compare"),
    path("compare/toggle/<int:id>/", views.toggle_compare, name="compare_toggle"),
    path("api/products/", views.product_api, name="product_api"),
]

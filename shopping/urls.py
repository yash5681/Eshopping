from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<slug:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<slug:product_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<int:order_id>/", views.order_success, name="order_success"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("profile/", views.profile, name="profile"),
    path("like/toggle/<slug:product_id>/", views.toggle_like, name="toggle_like"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
]
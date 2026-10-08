from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="admin_dashboard"),
    path("login/", views.admin_login_view, name="admin_login"),
    path("logout/", views.admin_logout_view, name="admin_logout"),

    # Products CRUD
    path("products/", views.product_list, name="admin_products"),
    path("products/add/", views.product_add, name="admin_product_add"),
    path("products/edit/<int:pk>/", views.product_edit, name="admin_product_edit"),
    path("products/delete/<int:pk>/", views.product_delete, name="admin_product_delete"),

    # Orders Management
    path("orders/", views.order_list, name="admin_orders"),
    path("orders/<int:pk>/", views.order_detail, name="admin_order_detail"),

    # Customers Management
    path("customers/", views.customer_list, name="admin_customers"),
    path("customers/delete/<int:pk>/", views.customer_delete, name="admin_customer_delete"),
]
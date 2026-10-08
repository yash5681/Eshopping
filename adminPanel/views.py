from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify

from shopping.models import Product, Category, Order, OrderItem, Register


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid username or password, or insufficient staff privileges.")

    return render(request, "adminPanel/login.html")


def admin_logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out of the Admin Panel.")
    return redirect("admin_login")


@user_passes_test(is_staff_user, login_url="admin_login")
def dashboard(request):
    total_customers = Register.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.exclude(status="Cancelled").aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    pending_orders = Order.objects.filter(status="Pending").count()

    recent_orders = Order.objects.order_by("-created_at")[:6]
    recent_customers = Register.objects.order_by("-id")[:5]
    featured_products = Product.objects.select_related("category").order_by("-id")[:5]

    context = {
        "active_tab": "dashboard",
        "total_customers": total_customers,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "recent_orders": recent_orders,
        "recent_customers": recent_customers,
        "featured_products": featured_products,
    }
    return render(request, "adminPanel/dashboard.html", context)


@user_passes_test(is_staff_user, login_url="admin_login")
def product_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    products = Product.objects.select_related("category").order_by("-id")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(badge__icontains=query))

    if category_slug:
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.all()

    context = {
        "active_tab": "products",
        "products": products,
        "categories": categories,
        "selected_category": category_slug,
        "query": query,
        "product_count": products.count(),
    }
    return render(request, "adminPanel/products.html", context)


@user_passes_test(is_staff_user, login_url="admin_login")
def product_add(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price", "0").strip()
        old_price = request.POST.get("old_price", "").strip() or None
        image = request.POST.get("image", "").strip()
        category_id = request.POST.get("category")
        tagline = request.POST.get("tagline", "").strip()
        badge = request.POST.get("badge", "").strip()
        stock = request.POST.get("stock", "10").strip()
        description = request.POST.get("description", "").strip()
        is_featured = request.POST.get("is_featured") == "on"

        if not name or not price or not image:
            messages.error(request, "Please fill in all required fields (Name, Price, Image URL).")
        else:
            category = Category.objects.filter(id=category_id).first() if category_id else None
            product = Product.objects.create(
                name=name,
                price=price,
                old_price=old_price,
                image=image,
                category=category,
                tagline=tagline,
                badge=badge,
                stock=int(stock) if stock.isdigit() else 10,
                description=description,
                is_featured=is_featured,
            )
            messages.success(request, f"Product '{product.name}' created successfully!")
            return redirect("admin_products")

    return render(request, "adminPanel/product_form.html", {
        "active_tab": "products",
        "categories": categories,
        "title": "Add New Product",
        "button_text": "Create Product",
    })


@user_passes_test(is_staff_user, login_url="admin_login")
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name", "").strip()
        product.price = request.POST.get("price", product.price)
        old_p = request.POST.get("old_price", "").strip()
        product.old_price = old_p if old_p else None
        product.image = request.POST.get("image", product.image).strip()
        category_id = request.POST.get("category")
        product.category = Category.objects.filter(id=category_id).first() if category_id else None
        product.tagline = request.POST.get("tagline", "").strip()
        product.badge = request.POST.get("badge", "").strip()
        stock = request.POST.get("stock", str(product.stock)).strip()
        product.stock = int(stock) if stock.isdigit() else product.stock
        product.description = request.POST.get("description", "").strip()
        product.is_featured = request.POST.get("is_featured") == "on"

        product.save()
        messages.success(request, f"Product '{product.name}' updated successfully!")
        return redirect("admin_products")

    return render(request, "adminPanel/product_form.html", {
        "active_tab": "products",
        "product": product,
        "categories": categories,
        "title": f"Edit Product: {product.name}",
        "button_text": "Save Changes",
    })


@user_passes_test(is_staff_user, login_url="admin_login")
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' was deleted successfully.")
        return redirect("admin_products")

    return render(request, "adminPanel/confirm_delete.html", {
        "active_tab": "products",
        "item_type": "Product",
        "item_name": product.name,
        "back_url": "admin_products",
    })


@user_passes_test(is_staff_user, login_url="admin_login")
def order_list(request):
    status_filter = request.GET.get("status", "").strip()
    query = request.GET.get("q", "").strip()

    orders = Order.objects.order_by("-created_at")

    if status_filter:
        orders = orders.filter(status=status_filter)

    if query:
        orders = orders.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(city__icontains=query) |
            Q(id__icontains=query)
        )

    status_counts = {
        "all": Order.objects.count(),
        "Pending": Order.objects.filter(status="Pending").count(),
        "Processing": Order.objects.filter(status="Processing").count(),
        "Shipped": Order.objects.filter(status="Shipped").count(),
        "Delivered": Order.objects.filter(status="Delivered").count(),
        "Cancelled": Order.objects.filter(status="Cancelled").count(),
    }

    context = {
        "active_tab": "orders",
        "orders": orders,
        "status_filter": status_filter,
        "query": query,
        "status_counts": status_counts,
        "status_choices": [s[0] for s in Order.STATUS_CHOICES],
    }
    return render(request, "adminPanel/orders.html", context)


@user_passes_test(is_staff_user, login_url="admin_login")
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
            return redirect("admin_order_detail", pk=order.id)

    return render(request, "adminPanel/order_detail.html", {
        "active_tab": "orders",
        "order": order,
        "status_choices": Order.STATUS_CHOICES,
    })


@user_passes_test(is_staff_user, login_url="admin_login")
def customer_list(request):
    query = request.GET.get("q", "").strip()
    customers = Register.objects.annotate(order_count=Count("orders")).order_by("-id")

    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile__icontains=query)
        )

    return render(request, "adminPanel/customers.html", {
        "active_tab": "customers",
        "customers": customers,
        "query": query,
        "customer_count": customers.count(),
    })


@user_passes_test(is_staff_user, login_url="admin_login")
def customer_delete(request, pk):
    customer = get_object_or_404(Register, pk=pk)
    if request.method == "POST":
        name = customer.name
        customer.delete()
        messages.success(request, f"Customer '{name}' removed successfully.")
        return redirect("admin_customers")

    return render(request, "adminPanel/confirm_delete.html", {
        "active_tab": "customers",
        "item_type": "Customer",
        "item_name": f"{customer.name} ({customer.email})",
        "back_url": "admin_customers",
    })

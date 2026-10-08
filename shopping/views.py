from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Register, Category, Product, Order, OrderItem, Review


def get_cart_data(request):
    cart = request.session.get("cart", {})
    cart_products = []
    total_amount = 0

    if cart:
        products = Product.objects.filter(slug__in=cart.keys())
        prod_map = {p.slug: p for p in products}

        for slug, quantity in list(cart.items()):
            product = prod_map.get(slug)
            if product and quantity > 0:
                subtotal = float(product.price) * quantity
                total_amount += subtotal
                cart_products.append({
                    "id": product.slug,
                    "slug": product.slug,
                    "name": product.name,
                    "price": product.price,
                    "image": product.image,
                    "quantity": quantity,
                    "subtotal": subtotal,
                    "stock": product.stock,
                })

    return {
        "cart_products": cart_products,
        "cart_count": sum(item["quantity"] for item in cart_products),
        "cart_total": total_amount,
    }


def home(request):
    search_query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    categories = Category.objects.all()
    products = Product.objects.select_related("category").order_by("-id")

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(badge__icontains=search_query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    cart_data = get_cart_data(request)

    liked_slugs = request.session.get("liked_products", [])
    liked_items = []
    if liked_slugs:
        liked_prods = Product.objects.filter(slug__in=liked_slugs)
        for p in liked_prods:
            liked_items.append({
                "id": p.slug,
                "slug": p.slug,
                "name": p.name,
                "price": p.price,
                "image": p.image,
            })

    deal_product = Product.objects.filter(is_featured=True).first()

    context = {
        "categories": categories,
        "products": products,
        "selected_category": category_slug,
        "search_query": search_query,
        "cart_count": cart_data["cart_count"],
        "cart_products": cart_data["cart_products"],
        "cart_total": cart_data["cart_total"],
        "liked_products": liked_slugs,
        "liked_items": liked_items,
        "liked_count": len(liked_items),
        "deal_product": deal_product,
    }
    return render(request, "index.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    reviews = product.reviews.all()
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    if not related_products.exists():
        related_products = Product.objects.exclude(pk=product.pk)[:4]

    cart_data = get_cart_data(request)
    liked_slugs = request.session.get("liked_products", [])

    # Handle submitting customer review
    if request.method == "POST" and "review_submit" in request.POST:
        user_name = request.POST.get("user_name", "").strip()
        rating = request.POST.get("rating", "5")
        comment = request.POST.get("comment", "").strip()

        if user_name and comment:
            Review.objects.create(
                product=product,
                user_name=user_name,
                rating=int(rating) if rating.isdigit() else 5,
                comment=comment
            )
            messages.success(request, "Thank you! Your product review has been submitted.")
            return redirect("product_detail", slug=product.slug)
        else:
            messages.error(request, "Please enter your name and review message.")

    # Calculate savings
    savings = None
    if product.old_price and product.old_price > product.price:
        savings = product.old_price - product.price

    context = {
        "product": product,
        "reviews": reviews,
        "related_products": related_products,
        "savings": savings,
        "cart_count": cart_data["cart_count"],
        "cart_products": cart_data["cart_products"],
        "cart_total": cart_data["cart_total"],
        "liked_products": liked_slugs,
        "liked_count": len(liked_slugs),
    }
    return render(request, "product_detail.html", context)


@require_POST
def add_to_cart(request, product_id):
    product = Product.objects.filter(slug=product_id).first()
    if product:
        try:
            qty = max(1, int(request.POST.get("quantity", 1)))
        except (ValueError, TypeError):
            qty = 1
        cart = request.session.get("cart", {})
        cart[product_id] = cart.get(product_id, 0) + qty
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, f"Added {qty} &times; '{product.name}' to your bag.")

    if request.POST.get("buy_now") == "1":
        return redirect("checkout")

    referer = request.META.get("HTTP_REFERER")
    return redirect(referer if referer else "home")


@require_POST
def update_cart_quantity(request, product_id):
    action = request.POST.get("action")
    cart = request.session.get("cart", {})

    if product_id in cart:
        if action == "increase":
            cart[product_id] += 1
        elif action == "decrease":
            if cart[product_id] > 1:
                cart[product_id] -= 1
            else:
                del cart[product_id]
        elif action == "remove":
            del cart[product_id]

        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart")


@require_POST
def toggle_like(request, product_id):
    product = Product.objects.filter(slug=product_id).first()
    if product:
        liked = request.session.get("liked_products", [])
        if product_id in liked:
            liked.remove(product_id)
            messages.info(request, f"Removed '{product.name}' from your wishlist.")
        else:
            liked.append(product_id)
            messages.success(request, f"Saved '{product.name}' to your wishlist!")
        request.session["liked_products"] = liked
        request.session.modified = True

    return redirect(request.META.get("HTTP_REFERER", "home"))


def wishlist(request):
    liked_slugs = request.session.get("liked_products", [])
    wishlist_items = []

    if liked_slugs:
        products = Product.objects.filter(slug__in=liked_slugs)
        for p in products:
            wishlist_items.append({
                "id": p.slug,
                "slug": p.slug,
                "name": p.name,
                "price": p.price,
                "image": p.image,
                "badge": p.badge,
            })

    cart_data = get_cart_data(request)

    return render(request, "wishlist.html", {
        "wishlist_items": wishlist_items,
        "wishlist_count": len(wishlist_items),
        "wishlist_total": sum(float(item["price"]) for item in wishlist_items),
        "cart_count": cart_data["cart_count"],
        "cart_products": cart_data["cart_products"],
        "cart_total": cart_data["cart_total"],
    })


def cart(request):
    cart_data = get_cart_data(request)
    return render(request, "cart.html", {
        "cart_items": cart_data["cart_products"],
        "cart_count": cart_data["cart_count"],
        "cart_total": cart_data["cart_total"],
    })


def checkout(request):
    cart_data = get_cart_data(request)
    if not cart_data["cart_products"]:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect("home")

    user_id = request.session.get("user_id")
    customer = Register.objects.filter(id=user_id).first() if user_id else None

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        payment_method = request.POST.get("payment_method", "Cash on Delivery")

        if not full_name or not email or not phone or not address or not city:
            messages.error(request, "Please fill in all required shipping fields.")
        else:
            order = Order.objects.create(
                customer=customer,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                postal_code=postal_code,
                payment_method=payment_method,
                total_amount=round(cart_data["cart_total"], 2),
                status="Pending"
            )

            for item in cart_data["cart_products"]:
                prod = Product.objects.filter(slug=item["slug"]).first()
                if prod:
                    if prod.stock >= item["quantity"]:
                        prod.stock -= item["quantity"]
                    else:
                        prod.stock = 0
                    prod.save(update_fields=['stock'])

                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    product_name=item["name"],
                    product_image=item["image"],
                    price=item["price"],
                    quantity=item["quantity"],
                    subtotal=round(item["subtotal"], 2)
                )

            # Clear cart
            request.session["cart"] = {}
            request.session.modified = True

            return redirect("order_success", order_id=order.id)

    return render(request, "checkout.html", {
        "cart_items": cart_data["cart_products"],
        "cart_count": cart_data["cart_count"],
        "cart_total": cart_data["cart_total"],
        "customer": customer,
    })


def order_success(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    return render(request, "order_success.html", {"order": order})


def my_orders(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.info(request, "Please login to view your order history.")
        return redirect("login")

    customer = Register.objects.filter(id=user_id).first()
    if not customer:
        request.session.flush()
        messages.warning(request, "Session expired or user not found. Please log in again.")
        return redirect("login")

    orders = Order.objects.filter(
        Q(customer=customer) | Q(email=customer.email)
    ).prefetch_related("items").order_by("-created_at")

    cart_data = get_cart_data(request)
    liked_slugs = request.session.get("liked_products", [])

    return render(request, "my_orders.html", {
        "customer": customer,
        "orders": orders,
        "cart_count": cart_data["cart_count"],
        "liked_count": len(liked_slugs),
    })


def profile(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.info(request, "Please login to access your account profile.")
        return redirect("login")

    customer = Register.objects.filter(id=user_id).first()
    if not customer:
        request.session.flush()
        messages.warning(request, "User account not found. Please log in again.")
        return redirect("login")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        if name and mobile:
            customer.name = name
            customer.mobile = mobile
            customer.save()
            request.session["user_name"] = name
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Name and mobile number cannot be blank.")

    orders_count = Order.objects.filter(Q(customer=customer) | Q(email=customer.email)).count()
    cart_data = get_cart_data(request)
    liked_slugs = request.session.get("liked_products", [])

    return render(request, "profile.html", {
        "customer": customer,
        "orders_count": orders_count,
        "cart_count": cart_data["cart_count"],
        "liked_count": len(liked_slugs),
    })


def login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = Register.objects.filter(email=email).first()

        if user and (check_password(password, user.password) or user.password == password):
            # Auto-upgrade plain text passwords to secure Django hash
            if not user.password.startswith(('pbkdf2_sha256$', 'argon2', 'bcrypt')):
                user.password = make_password(password)
                user.save(update_fields=['password'])

            request.session["user_name"] = user.name
            request.session["user_id"] = user.id
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect("home")

        return render(request, "login.html", {
            "error": "Invalid email or password"
        })

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        mobile = request.POST.get("mobile", "").strip()

        if not name or not email or not password or not mobile:
            return render(request, "register.html", {
                "error": "All fields are required."
            })

        if password != confirm_password:
            return render(request, "register.html", {
                "error": "Passwords do not match."
            })

        if Register.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "error": "An account with this email already exists."
            })

        user = Register.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            mobile=mobile
        )
        request.session["user_name"] = user.name
        request.session["user_id"] = user.id
        messages.success(request, f"Welcome to E-Shop, {user.name}! Account created.")
        return redirect("home")

    return render(request, "register.html")


def logout(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect("home")

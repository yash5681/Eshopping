from django.contrib import admin
from .models import Register, Category, Product, Order, OrderItem, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user_name', 'comment')


@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'mobile', 'created_at')
    search_fields = ('name', 'email', 'mobile')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock', 'badge', 'is_featured')
    list_filter = ('category', 'is_featured', 'badge')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'city')
    inlines = [OrderItemInline]
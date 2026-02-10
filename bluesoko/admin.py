from django.contrib import admin

# Register your models here.

from .models import Shop,Product,ProductImage, Category, Order, OrderItem,ShopRating


# ---------- INLINES FIRST ----------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    
# ---------- MODEL ADMINS ----------    
admin.site.register(Category)
admin.site.register(OrderItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
    inlines = [OrderItemInline]
    
    
# admin.site.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name',)
    inlines = [ProductImageInline]
    
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('name', 'owner__username')


admin.site.register(Product, ProductAdmin)

# admin.site.register(ShopRating)
# @admin.register(ShopRating)
# class ShopRatingAdmin(admin.ModelAdmin):
#     list_display = ('shop', 'user', 'rating', 'created_at')
#     list_filter = ('rating', 'created_at')
#     search_fields = ('shop__name', 'user__username')

@admin.register(ShopRating)
class ShopRatingAdmin(admin.ModelAdmin):
    list_display = ('shop', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('shop__name', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('shop', 'user')

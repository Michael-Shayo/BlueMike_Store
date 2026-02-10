from django.contrib import admin
from .models import User,Profile,SellerProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'status', 'is_active')
    list_filter = ('role', 'status')
    search_fields = ('username', 'email', 'phone')

admin.site.register(Profile)
admin.site.register(SellerProfile)
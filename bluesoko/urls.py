from django.urls import path
from . import views

from django.contrib.sitemaps.views import sitemap
from .sitemaps import ProductSitemap, CategorySitemap, ShopSitemap, StaticViewSitemap
sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'shops': ShopSitemap,
}


app_name = 'bluesoko'

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django-sitemap'),
    
    path('', views.home, name='home'),
    path('product_list', views.product_list, name='product_list'),
    # path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    # path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('shop/<slug:slug>/', views.shop_detail, name='shop_detail'),
    path('apply/', views.apply_shop, name='apply_shop'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout, name='checkout'),
    # path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('seller/order-item/<int:item_id>/status/', views.update_order_item_status, name='update_order_item_status'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shop/<int:shop_id>/rate/', views.rate_shop, name='rate_shop'),




]

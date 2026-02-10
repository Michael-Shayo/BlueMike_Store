from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Category, Shop

class StaticViewSitemap(Sitemap):
    """For static pages like home, about, contact"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['bluesoko:home', 'bluesoko:product_list']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Sitemap for active products"""
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("bluesoko:product_detail", args=[obj.slug])

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    """Sitemap for active categories"""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("bluesoko:product_list") + f"?category={obj.slug}"


class ShopSitemap(Sitemap):
    """Sitemap for approved shops"""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Shop.objects.filter(is_approved=True)

    def location(self, obj):
        return reverse("bluesoko:shop_detail", args=[obj.slug])

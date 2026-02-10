from decimal import Decimal
from django.db import transaction
from django.contrib import  messages
from django.utils.text import slugify
from django.db.models.functions import Ln
from django.db.models import Count, Q, Avg
from django.db.models import FloatField, ExpressionWrapper, F
from django.db.models.functions import Log
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Shop, Product, ProductImage, Order, OrderItem, Category, ShopRating

# Create your views here.
from django.db.models import Count, Avg, FloatField, F, ExpressionWrapper
from django.db.models.functions import Ln

def home(request):
    top_selling = (
        Product.objects
        .annotate(sales=Count('orderitem', distinct=True))
        .order_by('-sales')[:8]
    )
    top_categories = (
        Product.objects
        .select_related("category")
        .values("category__slug", "category__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:4]
    )
    new_arrivals = Product.objects.order_by('-created_at')[:8]

    # Top-rated shops: use weighted_score
    top_rated_shops = (
        Shop.objects
        .filter(is_approved=True)
        .annotate(
            rating_count=Count('ratings', distinct=True),
            avg_rating=Avg('ratings__rating'),
        )
        .annotate(
            weighted_score=ExpressionWrapper(
                F('avg_rating') * Ln(F('rating_count') + 1),
                output_field=FloatField()
            )
        )
        # Only show shops with at least 10 ratings and avg rating >= 4.5
        .filter(rating_count__gte=10, avg_rating__gte=4.5)
        .order_by('-weighted_score', '-avg_rating', '-rating_count')[:6]
    )

    context = {
        'top_selling': top_selling,
        'new_arrivals': new_arrivals,
        "top_categories": top_categories,
        'top_rated_shops': top_rated_shops,
    }
    return render(request, 'bluesoko/home.html', context)


@login_required
def apply_shop(request):
    if request.user.role != 'seller':
        messages.info(request, "You must be a seller to apply for a shop")
        return redirect('bluesoko:home')
    registered_shop = Shop.objects.filter(owner=request.user).first()
    if registered_shop:
        messages.info(request, "You already applied or own a shop")
        return redirect('bluesoko:home')
    if request.method == 'POST':
        name = request.POST.get('shop_name')
        location = request.POST.get('location')
        description = request.POST.get('description')
        phone = request.POST.get('phone')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        latitude = float(latitude) if latitude else None
        longitude = float(longitude) if longitude else None
        if not name or not location or not phone:
            messages.error(request, "Please fill all required fields")
            return redirect('bluesoko:apply_shop')
        with transaction.atomic():
            Shop.objects.create(
                owner= request.user,
                name= name,
                location=location,
                description=description,
                phone=phone,
                latitude=latitude or None,
                longitude=longitude or None,
            )
            messages.success(request, "Shop application submitted successfully.")
            return redirect('bluesoko:seller_dashboard')
    return render(request, 'bluesoko/apply_shop.html')


@login_required
def add_product(request):
    try:
        shop = Shop.objects.get(owner=request.user)
    except Shop.DoesNotExist:
        messages.error(request, "You must create a shop before adding products.")
        return redirect('bluesoko:apply_shop')
    if not shop.is_approved:
        messages.warning(request,"Your shop is pending approval. You cannot add products yet.")
        return redirect('bluesoko:seller_dashboard')
    # ✅ ALWAYS define this (GET + POST)
    categories = Category.objects.filter(is_active=True)
    if request.method == 'POST':
        name = request.POST.get('name')
        try:
            price = Decimal(request.POST.get('price'))
        except:
            messages.error(request, "Invalid price value.")
            return render(request, 'bluesoko/add_product.html', {
                'categories': categories
            })
        stock = int(request.POST.get('stock', 1))
        description = request.POST.get('description')
        category_name = request.POST.get('category')
        negotiable = bool(request.POST.get('negotiable'))
        if not name or not price or not category_name:
            return render(request, 'bluesoko/add_product.html', {
                'categories': categories,
                'error': 'All fields are required'
            })
        category = Category.objects.filter(
            name__iexact=category_name).first()
        if not category:
            category = Category.objects.create(
                name=category_name,
                slug=slugify(category_name)
            )
        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock or 1,
            negotiable=negotiable,
            description= description,
            seller=request.user,
            shop=shop,
            category=category, 
        )
        for img in request.FILES.getlist('images'):
            ProductImage.objects.create(
                product=product,
                image=img
            )
        messages.success(request, "Product added successfully.")
        return redirect('bluesoko:seller_dashboard')
    return render(request, 'bluesoko/add_product.html', {'categories': categories})


@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        messages.error(request, "Sorry you must be a seller to view this.")
        return redirect('bluesoko:home')
    try:
        shop = Shop.objects.get(owner=request.user)
    except Shop.DoesNotExist:
        messages.error(request, "You don't have a shop yet.")
        return redirect('bluesoko:home')
    products = Product.objects.filter(shop=shop)
    return render(request, 'bluesoko/dashboard.html', {'shop': shop, 'products': products})


def product_list(request):
    products = Product.objects.filter(is_active=True)
    query = request.GET.get('q')
    search_type = request.GET.get('type', 'all')
    if query:
        if search_type == 'product':
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        elif search_type == 'shop':
            products = products.filter(
                shop__name__icontains=query
            )
        else:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(shop__name__icontains=query)
            )
    # CATEGORY FILTER
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__slug__in=selected_categories)
    # PRICE FILTER
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__lte=Decimal(max_price))
    # 🔥 THIS IS THE KEY LINE
    categories = Category.objects.annotate(
        product_count=Count(
            'products',
            filter=Q(products__is_active=True)
        )
    )
    context = {
        'products': products,
        'categories': categories,
        'selected_categories': selected_categories,
        'min_price': min_price or 2000,
        'max_price': max_price or 1000000,
        'query': query
    }
    return render(request, 'bluesoko/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )
    return render(request, 'bluesoko/product_detail.html', {'product': product})


def shop_detail(request, slug):
    try:
        shop = Shop.objects.get(slug=slug)
    except Shop.DoesNotExist:
        return render(request, 'bluesoko/shop_status.html', {
            'status': 'not_found',
            'owner_view': False,
        }, status=404)
    # shop exists but not approved (owner view)
    if not shop.is_approved and request.user == shop.owner:
        return render(request, 'bluesoko/shop_status.html', {
            'status': 'pending',
            'shop': shop,
            'owner_view': True
        })
    # shop exists but not approved (public view)
    if not shop.is_approved:
        return render(request, 'bluesoko/shop_status.html', {
            'status': 'pending',
            'shop': shop,
            'owner_view': False
        }, status=403)
    products = shop.products.filter(is_active=True)
    return render(request, 'bluesoko/shop_detail.html', {'shop': shop,'products': products})


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if request.user.is_authenticated and request.user.role == 'seller':
        # product.shop.owner assumes Product → Shop → owner
        if product.shop.owner == request.user:
            messages.error(
                request,
                "You cannot buy products from your own shop."
            )
            return redirect('bluesoko:product_detail', slug=slug)
    if product.stock < 1:
        messages.error(request, "Sorry This product is out of stock contact a seller.")
        return redirect('bluesoko:product_detail', slug=slug)
    cart = request.session.get('cart', {})
    product_id = str(product.id)
    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.images.first().image.url if product.images.exists() else ''
        }
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, "Product added to cart")
    return redirect('bluesoko:cart')


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, "Your cart is empty.")
        return render(request, 'bluesoko/cart.html')
    total = sum(
        Decimal(item['price']) * item['quantity']
        for item in cart.values()
    )
    return render(request, 'bluesoko/cart.html', {
        'cart': cart,
        'total': total
    })


@require_POST
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        quantity = max(1, int(request.POST.get('quantity', 1)))
        cart[product_id]['quantity'] = quantity
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('bluesoko:cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('bluesoko:cart')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('bluesoko:cart')
    if request.method == "GET":
        return render(request, 'bluesoko/checkout.html')
    products = Product.objects.select_for_update().filter(
        id__in=cart.keys()
    )
    try:
        with transaction.atomic():
            # 🚨 VALIDATIONS FIRST
            for product in products:
                if product.seller == request.user:
                    raise Exception("You cannot buy your own product")
                if cart[str(product.id)]['quantity'] > product.stock:
                    raise Exception(f"Not enough stock for {product.name}")
            phone=request.POST.get('phone')
            address=request.POST.get('address')
            if not phone or not address:
                messages.error(request, "Phone and address are required.")
                return redirect('bluesoko:checkout')
            # 🧾 CREATE ORDER
            order = Order.objects.create(
                user=request.user,
                phone=phone,
                address=address,
                total = Decimal('0.00')
            )
            total = Decimal('0.00')
            # 📦 CREATE ORDER ITEMS + UPDATE STOCK
            for product in products:
                quantity = cart[str(product.id)]['quantity']
                price = product.price * quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    seller=product.seller,
                    quantity=quantity,
                    price=price
                )
                product.stock = max(0, product.stock - quantity)
                product.save(update_fields=['stock'])
                total += price
            order.total = total
            order.save()
    except Exception as e:
        messages.error(request, str(e))
        return redirect('bluesoko:cart')
    # 🧹 CLEAN CART
    request.session['cart'] = {}
    messages.success(request, "Order placed successfully!")
    return redirect('bluesoko:home')


@login_required
def update_order_item_status(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, seller=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if item.status == 'completed':
            messages.warning(request, "This order item is already completed.")
            return redirect('bluesoko:seller_orders')
        if new_status:
            item.status = new_status
            item.save()
        order = item.order
        # ✅ USE related_name='items'
        statuses = order.items.values_list('status', flat=True)
        # Auto update order status
        if all(s == 'completed' for s in statuses):
            order.status = 'completed'
        elif all(s == 'rejected' for s in statuses):
            order.status = 'cancelled'
        elif 'accepted' in statuses:
            order.status = 'accepted'
        else:
            order.status = 'pending'
        order.save()
        messages.success(request, "Order status updated.")
    return redirect('bluesoko:seller_orders')


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bluesoko/my_orders.html', {'orders': orders})


@login_required
def seller_orders(request):
    if request.user.role != 'seller':
        messages.error(request, "You are not allowed to access seller pages.")
        return redirect('bluesoko:product_list')
    order_items = OrderItem.objects.filter(
        seller=request.user
    ).select_related('order', 'product', 'order__user').order_by('-order__created_at')
    return render(request, 'bluesoko/seller_orders.html', {'order_items': order_items})


def shop_list(request):
    query = request.GET.get('q')
    location = request.GET.get('location')

    shops = (
        Shop.objects
        .filter(is_approved=True)
        .annotate(
            # product_count=Count('products',distinct=True),
            rating_count=Count('ratings', distinct=True),
            avg_rating=Avg('ratings__rating'),
        )
        .annotate(
            weighted_score=ExpressionWrapper(
                F('avg_rating') * Log(F('rating_count') + 1, 10),
                output_field=FloatField()
            )

        )
        .order_by('-weighted_score', '-avg_rating', '-rating_count')
    )
    
    if query:
        shops = shops.filter(name__icontains=query)

    if location:
        shops = shops.filter(location__icontains=location)

    locations = (
        Shop.objects
        .filter(is_approved=True)
        .values_list('location', flat=True)
        .distinct()
    )
    return render(request, 'bluesoko/shop_list.html', {
        'shops': shops,
        'locations': locations,
        'query': query,
        'selected_location': location,
    })


@login_required
def rate_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.user.role == 'seller':
        messages.error(request, "Sellers cannot rate shops.")
        return redirect('bluesoko:shop_detail', slug=shop.slug)
    
    if shop.owner == request.user:
        messages.error(request, "You cannot rate your own shop.")
        return redirect('bluesoko:shop_detail', slug=shop.slug)
    
    has_bought = OrderItem.objects.filter(
                order__user=request.user,
                product__shop=shop,
                status='completed').exists()

    if not has_bought:
        messages.error(request, "You can only rate shops you bought from.")
        return redirect('bluesoko:shop_detail', slug=shop.slug)
    
    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        ShopRating.objects.update_or_create(
            shop=shop,
            user=request.user,
            defaults={"rating": rating}
        )
        messages.success(request, "Thank you for rating!")
    return redirect('bluesoko:shop_detail', slug=shop.slug)


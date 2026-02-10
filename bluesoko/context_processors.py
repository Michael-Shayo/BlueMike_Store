def cart_counter(request):
    cart = request.session.get('cart', {})

    # cart example: { "1": {"quantity": 2}, "5": {"quantity": 1} }
    cart_count = sum(item.get('quantity', 1) for item in cart.values())

    return {
        'cart_count': cart_count
    }

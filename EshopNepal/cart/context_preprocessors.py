from .models import Cart, CartItem
from cart.views import _sessionId

def counter(request):
    count =0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_sessionId(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for i in cart_items:
                count += i.quantity
        except Cart.DoesNotExist:
            count = 0
    return dict(cart_count = count)
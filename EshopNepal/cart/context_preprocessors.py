from store.views import wishlist
from .models import Cart, CartItem
from cart.views import _sessionId
from store.models import WishList

def counter(request):
    count =0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_sessionId(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)    
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for i in cart_items:
                count += i.quantity
        except Cart.DoesNotExist:
            count = 0
    return dict(cart_count = count)

def wishlist_counter(request):
    if 'admin' in request.path:
        return {}
    else:
        wishlist = WishList.objects.filter(user__id=request.user.id)
        if wishlist is not None:
            wish_count = len(wishlist)

    return dict(wish_count=wish_count)
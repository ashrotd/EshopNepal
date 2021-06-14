from django.http.response import HttpResponse
from store.models import Product
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist
from .models import Cart, CartItem
from store.models import Variation


# Create your views here.
def _sessionId(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for i in request.POST:
            key = i
            value = request.POST[key]
            try:
                variations = Variation.objects.get(products=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variations)
            except:
                pass
    
    try:
        cart = Cart.objects.get(cart_id = _sessionId(request)) #Get the cart using the Session id as cart id
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_sessionId(request))
    cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity +=1 # cart_item.quantity is equal to existing +1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity = 1
        )
        cart_item.save()
    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_sessionId(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity >1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_sessionId(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0,quantity=0, cart_items=None):
    try:
        total_tax =0
        cart = Cart.objects.get(cart_id=_sessionId(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for i in cart_items:
            total += (i.product.price*i.quantity)
            quantity += i.quantity
        total_tax = total*0.13+total
    except ObjectDoesNotExist:
        pass
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'total_tax':total_tax
    }    
    return render(request, 'store/cart.html',context) 
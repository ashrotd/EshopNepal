from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem
from store.models import Product, Variation
# Create your views here.


def _sessionId(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []
    if request.method == 'POST':
        for i in request.POST:
            key = i
            value = request.POST[key]

            try:
                variations = Variation.objects.get(
                    products=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variations)
                print(product_variations)

            except Exception as e:
                pass

    try:
        cart = Cart.objects.get(cart_id=_sessionId(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_sessionId(request))
    cart.save()

    cart_exist = CartItem.objects.filter(cart=cart, product=product).exists()
    if cart_exist:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        id = []
        for i in cart_item:
            existing_variation = i.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(i.id)
        
        if product_variations in ex_var_list:
            index = ex_var_list.index(product_variations)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variations)>0:
                item.variations.clear()
                item.variations.add(*product_variations)
            item.save()

    else:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1,
        )
        if len(product_variations) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_sessionId(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
         cart_item.quantity -= 1
         cart_item.save()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_sessionId(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_sessionId(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for i in cart_items:
            total += (i.product.price*i.quantity)
            quantity += i.quantity
        total_tax = total*0.13+total
    except NameError:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'total_tax': total_tax
    }
    return render(request, 'store/cart.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from cart.models import CartItem, Cart
from cart.views import _sessionId, cart
from django.http import HttpResponse
# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available=True)
        count = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        count = products.count()
    context = {
        'products':products,
        'count':count 
    }
    return render(request,'store/store.html', context)

def product_detail(request, product_slug, category_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_sessionId(request), product=single_product).exists()
        
    except Exception as e:
        raise e

    context = {
        'single_product':single_product,
        'in_cart':in_cart
    }
    return render(request, 'store/product_detail.html',context)
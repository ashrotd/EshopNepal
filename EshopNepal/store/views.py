from django.core import paginator
from django.shortcuts import redirect, render, get_object_or_404
from .models import Product, Category
from cart.models import CartItem, Cart
from django.db.models import Q
from django.contrib import messages
from cart.views import _sessionId, cart
from .forms import ReviewForm
from .models import ReviewSystem
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        count = products.count()
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        count = products.count()
    context = {
        'products':paged_products,
        'count':count 
    }
    return render(request,'store/store.html', context)

def product_detail(request, product_slug, category_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_sessionId(request), product=single_product).exists()
        
    except Exception as e:
        raise e

    reviews = ReviewSystem.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'reviews':reviews,
    }
    return render(request, 'store/product_detail.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword != ' ':
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            count = products.count()
    context ={'products':products, 'count':count}    
    return render(request, 'store/store.html',context)

def submit_review(request, product_id):
    url =request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        
        try: 
            reviews = ReviewSystem.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request,'Thank You, Review has been Updated!!!')
            return redirect(url)
        except ReviewSystem.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewSystem()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,'Thank You for Reviewing !!!')
                return redirect(url)
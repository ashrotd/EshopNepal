from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product
from store.models import ReviewSystem
# Create your views here.
def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_date')
    for i in products:
        reviews = ReviewSystem.objects.filter(product_id=i.id, status=True)
    context = {
        'products':products,
        'reviews':reviews,
    }
    return render(request, 'home.html', context)
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
import datetime
from .forms import OrderForm
from orders.models import Order, Payment
from cart.models import CartItem
import json

# Create your views here.
def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    return render(request,'orders/payment.html')



def place_order(request, total =0, quantity=0):
    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items.count() <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for i in cart_items:
        total += (i.product.price*i.quantity)
        quantity += i.quantity
        tax = total*0.13
        grand_total = total+tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
    
        if form.is_valid():
            data = Order()
            data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone_number = form.cleaned_data['phone_number']
            data.email = form.cleaned_data['email']
            data.address_line1 = form.cleaned_data['address_line1']
            data.address_line2 = form.cleaned_data['address_line2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_num = current_date + str(data.id)
            data.order_number = order_num
            data.save()

            order = Order.objects.get(user = request.user, is_ordered=False, order_number=order_num)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'grand_total':grand_total,
                'tax':tax,
            }
            return render(request,'orders/payment.html',context)

    else:
        return redirect('checkout')

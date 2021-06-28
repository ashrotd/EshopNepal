from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
import datetime
from .forms import OrderForm
from orders.models import Order, OrderItem, Payment
from cart.models import CartItem
from store.models import Product
import json

# email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message


# Create your views here.
def paypal_payment(request):
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

    cart_items = CartItem.objects.filter(user=request.user)
    # Populating OrderItem Table
    for i in cart_items:
        order_item = OrderItem()
        order_item.order_id = order.id
        order_item.payment = payment
        order_item.user_id = request.user.id
        order_item.product_id = i.product_id
        order_item.quantity = i.quantity
        order_item.product_price = i.product.price
        order_item.ordered = True
        order_item.save()

        # About Variations in OrderItem Table
        cart_item = CartItem.objects.get(id=i.id)
        product_variation = cart_item.variations.all()
        order_item = OrderItem.objects.get(id=order_item.id)
        order_item.variation.set(product_variation)
        order_item.save()

        # Decrease Stocks of product
        product = Product.objects.get(id=i.product_id)
        product.stock -= i.quantity  
        product.save()

        # clear CartItem
    CartItem.objects.filter(user=request.user).delete()

        #send Email to costumers
    mail_subject = "Thank you for ordering the Items !!!"
    message = render_to_string('orders/order_received.html',{
                'user':request.user,
                'order':order,
                'date':datetime.date.today() + datetime.timedelta(days=1),
            })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()

    # Send Order Number and Details to the page back
    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,
    }
    return JsonResponse(data)

def cod(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment(
        user = request.user,
        payment_id = 'COD',
        payment_method = 'COD',
        amount_paid = order.order_total,
        status = "COMPLETED"
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    cart_items = CartItem.objects.filter(user=request.user)
    # Populating OrderItem Table
    for i in cart_items:
        order_item = OrderItem()
        order_item.order_id = order.id
        order_item.payment = payment
        order_item.user_id = request.user.id
        order_item.product_id = i.product_id
        order_item.quantity = i.quantity
        order_item.product_price = i.product.price
        order_item.ordered = True
        order_item.save()

        # About Variations in OrderItem Table
        cart_item = CartItem.objects.get(id=i.id)
        product_variation = cart_item.variations.all()
        order_item = OrderItem.objects.get(id=order_item.id)
        order_item.variation.set(product_variation)
        order_item.save()

        # Decrease Stocks of product
        product = Product.objects.get(id=i.product_id)
        product.stock -= i.quantity  
        product.save()

        # clear CartItem
    CartItem.objects.filter(user=request.user).delete()

        #send Email to costumers
    mail_subject = "Thank you for ordering the Items !!!"
    message = render_to_string('orders/order_received.html',{
                'user':request.user,
                'order':order,
                'date':datetime.date.today() + datetime.timedelta(days=1),
            })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()
    # Send Order Number and Details to the page back
    data = {
        'order_number' : order.order_number,
        'transID' : payment.payment_id,
    }
    return JsonResponse(data)


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

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('paymentID')
    if transID != 'COD':
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            order_items = OrderItem.objects.filter(order_id=order.id)
            payment = Payment.objects.get(payment_id=transID)
            sub_total = 0
            for i in order_items:
                sub_total += i.product_price
            context = {
                'order':order,
                'payment':payment.status,
                'order_items':order_items,
                'order_number':order.order_number,
                'sub_total':sub_total,
                'transID':payment.payment_id,
            }
            return render(request, 'orders/order_complete.html', context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('home')
    else:
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            order_items = OrderItem.objects.filter(order_id=order.id)
            sub_total = 0
            for i in order_items:
                sub_total += i.product_price
            context = {
                'order':order,
                'payment':'Completed by COD',
                'order_items':order_items,
                'order_number':order.order_number,
                'sub_total':sub_total,
                'transID':'COD',
            }
            return render(request, 'orders/order_complete.html', context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('home')
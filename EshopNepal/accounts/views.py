from django.contrib import messages, auth
from django.http.request import QueryDict
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django import http
from django.http.response import HttpResponse
import requests
from django.shortcuts import redirect, render
from .forms import RegisterForm
from cart.models import Cart, CartItem
from cart.views import _sessionId

#email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()
            # Sending Email
            current_site = get_current_site(request)
            mail_subject = "Email Verification"
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            #messages.success(request,'Registration is Successful !!! Veriy your email address !')
            return redirect('/account/login/?command=verification&email='+ email)
    else:      
        form = RegisterForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/register.html',context)

def login(request):
      
    if request.method == 'POST':
        email = request.POST['email']   
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:  
            try:
                cart = Cart.objects.get(cart_id = _sessionId(request))
                cart_exists = CartItem.objects.filter(cart=cart).exists()
                if cart_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    # Getting Product Variation by cart-id
                    product_variation = []
                    for i in cart_item:
                        variation = i.variations.all()
                        product_variation.append(list(variation))

                    # excess cartitem from user
                    cart_item = CartItem.objects.filter(user=user)
                    existing_list = []
                    id = []
                    for i in cart_item:
                        existing_variation = i.variations.all()
                        existing_list.append(list(existing_variation))
                        id.append(i.id)
                    
                    for p in product_variation:
                        if p in existing_list:
                            index = existing_list.index(p)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
                    # for i in cart_item:
                    #    i.user = user
                    #    i.save() 
            except:
                pass
            auth.login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print('query ->',query)
                # Django given url of login required : next=/cart/checkout/ 
                split_param = dict(x.split('=') for x in query.split('&'))
                print(split_param)
                if 'next' in split_param:
                    goto_page =  split_param['next']
                    return redirect(goto_page)
            except:
                return redirect('home')            
        else:
            messages.error(request, 'Invalid Email or Password')    
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are Logged Out !!!')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid) 
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account is Activated !!!')
        return redirect('login')
    else:
        messages.error(request, 'Activation Failed, Try Again !!!')
        return redirect('register')
    
@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            # Forgot Password
            current_site = get_current_site(request)
            mail_subject = "Password Recovery Mail"
            message = render_to_string('accounts/reset_password.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request, "Password reset email is sent to your Email Address")
            return redirect('login')
        else:
            messages.error(request,'Email Does not Exist')
            return redirect('forgotpassword')
    return render(request,'accounts/forgotpassword.html')

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid) 
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please Reset Your Password')
        return redirect('reset_password_page')
    else:
        messages.error(request,'This link is expired !!!')
        return redirect('login')

def reset_password_page(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password is Changed, Login Now !!!')
            return redirect('login')
        else:
            messages.error(request, 'Password Donot Match')
            return redirect('reset_password_page')
    
    else:
        return render(request,'accounts/reset_password_page.html')
     
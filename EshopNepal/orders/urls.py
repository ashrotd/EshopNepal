from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name = 'place_order'),
    path('paypal_payment/', views.paypal_payment, name='paypal_payment'),
    path('cash_on_delivery/', views.cod, name='cod'),
    path('order_complete/', views.order_complete, name='order_complete')
]

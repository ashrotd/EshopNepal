
from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/',views.logout, name='logout'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('forgotpassword/',views.forgotpassword, name='forgotpassword'),
    path('reset_password/<uidb64>/<token>/',views.reset_password, name='reset_password'),
    path('reset_password_page/',views.reset_password_page,name='reset_password_page'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_password/', views.edit_password, name='edit_password'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details')

] 

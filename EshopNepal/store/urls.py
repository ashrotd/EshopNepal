
from django.urls import path
from . import views
import store

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name = 'products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name = 'product_detail'),
    path('search', views.search, name='search'),
    path('submit_review/<int:product_id>/',views.submit_review, name='submit_review'),
    path('wishlist_input/<int:product_id>/', views.wishlist_input, name='wishlist_input'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_wishlist/<int:product_id>/', views.remove_wishlist, name='remove_wishlist')
] 

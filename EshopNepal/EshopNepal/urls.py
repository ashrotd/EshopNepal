
from django import urls
import store
from EshopNepal.settings import MEDIA_ROOT
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
] + static(settings.MEDIA_URL, document_root = MEDIA_ROOT)

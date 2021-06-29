from django.contrib import admin
from django.db import models
from .models import Product
from .models import ReviewSystem
from .models import Variation
from .models import ProductGallery
import admin_thumbnails
# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','category', 'price', 'stock','modified_date')
    prepopulated_fields ={'slug':('product_name',)}
    inlines = [ProductGalleryInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('products','variation_category','variation_value','is_active')
    list_editable = ('is_active',)
    list_filter = ('products','variation_category','variation_value')

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewSystem)
admin.site.register(ProductGallery)
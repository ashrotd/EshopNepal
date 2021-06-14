from django.contrib import admin
from django.db import models
from .models import Product
from .models import Variation
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','category', 'price', 'stock','modified_date')
    prepopulated_fields ={'slug':('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('products','variation_category','variation_value','is_active')
    list_editable = ('is_active',)
    list_filter = ('products','variation_category','variation_value')

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation, VariationAdmin)
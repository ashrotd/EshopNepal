from django.contrib import admin
from .models import Payment, Order, OrderItem

class InlineOrderItem(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('payment','product','quantity','product_price','ordered',)
# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','email','phone_number','address','status','is_ordered','created_date']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number','first_name','last_name','phone_number','email']
    list_per_page = 25
    inlines = [InlineOrderItem]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
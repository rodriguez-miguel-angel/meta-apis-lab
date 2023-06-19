from django.contrib import admin

# Register your models here.
from .models import Category, MenuItem, Cart, Order, OrderItem

# Register your models here.
# admin.site.register(Category)
class CartAdmin(admin.ModelAdmin):
  list_display = ("user", "menu_item", "quantity",)

admin.site.register(MenuItem)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)


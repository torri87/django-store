from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Order, Product, Category, OrderItem

admin.site.register(User, UserAdmin)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(OrderItem)
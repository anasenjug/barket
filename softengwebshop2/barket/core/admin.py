from django.contrib import admin
from .models import Profile, Product, CartItem, Contact, Order, Ticket, TopUpCode

# Register your models here.

admin.site.register(CartItem)
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(TopUpCode)
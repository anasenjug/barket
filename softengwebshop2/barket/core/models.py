from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User
from django.utils import timezone
from django.db.models import Q
import shortuuid
from django.db.models.signals import post_save
from django.dispatch import receiver
import core.signals
# Create your models here.



class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.FloatField()
    image = models.CharField(max_length=500)

    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.user.first_name | self.balance
    

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f'{self.quantity} x {self.product.name} | {self.user.first_name}'
    
class Contact(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return 'Message from ' + self.email

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        total_price = (self.product.price * self.quantity)
        return f'{self.user} | {self.date_ordered} | {total_price}'

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.user.username}"

class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content}"

def generate_ref_code():
    short_uuid = shortuuid.ShortUUID().random()
    truncated_uuid = short_uuid[:12]
    return truncated_uuid 

class TopUpCode(models.Model):
    ref_code = models.CharField(max_length=12, default=generate_ref_code, unique=True, primary_key=True, editable=False)
    exp_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ref_code} - {self.amount}"

class TopUpTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topup_transactions')
    top_up_code = models.ForeignKey(TopUpCode, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


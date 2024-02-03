from datetime import date
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import View
from .forms import RegisterForm, UpdateUserForm,TopUpCodeForm
from django.contrib.auth.views import LoginView
from .forms import RegisterForm, LoginForm, ContactForm
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Order, TopUpCode, TopUpTransaction
from django.http import HttpResponse,Http404	
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils import timezone
import core.signals
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test


# Create your views here.

def index(request):
    context = {}
    return render(request, 'core/index.html', context)

def products(request):
    context = Product.objects.all()
    
    return render(request, 'core/products.html', {'products': context})

@never_cache
def view_cart(request):
    context = {}
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'core/cart.html', {'cart_items': cart_items, 'total_price': total_price})
    else:
        return render(request, 'core/index.html', context)

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, 
                                                       user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('app:view_cart')
 
def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('app:view_cart')

def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        new_order = Order.objects.create(user=request.user, product=item.product)
        new_order.date_ordered = date.today()
        new_order.quantity = item.quantity
        new_order.save()
    cart_items.delete()
    return redirect('app:orders')

def orders(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.is_staff:
            orders = Order.objects.all()
            return render(request, 'core/orders.html', {'order': orders})
        context = {"order": Order.objects.filter(user=request.user, date_ordered=date.today())}
        return render(request, 'core/orders.html', context)
    else:
        return render(request, 'core/index.html', context)



class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'core/register.html'
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect(to='/')
        return render(request, self.template_name, {'form': form})

class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)
    
@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='/profile')
    else:
        user_form = UpdateUserForm(instance=request.user)


    return render(request, 'core/profile.html', {'user_form': user_form})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:success')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})

def success(request):
    return HttpResponse('Success! Thank you for your message.')

def about(request):
    return render(request, 'core/about.html')


@login_required
def top_up(request):
    if request.method == 'POST':
        form = TopUpCodeForm(request.POST)
        if form.is_valid():
            top_up_code = form.cleaned_data['ref_code']
            try:
                code_obj = TopUpCode.objects.get(ref_code=top_up_code)

                if code_obj.is_used:
                    messages.error(request, 'This top-up code has already been used.')
                elif code_obj.exp_date < timezone.now():
                    messages.error(request, 'This top-up code has expired.')
                else:
                    # Update user's balance and mark the code as used
                    request.user.profile.balance += code_obj.amount
                    request.user.profile.save()
                    code_obj.is_used = True
                    code_obj.save()

                    # Create a top-up transaction record
                    TopUpTransaction.objects.create(user=request.user, top_up_code=code_obj)

                    messages.success(request, f'Successfully topped up {code_obj.amount}!')
                    return redirect('app:profile')

            except TopUpCode.DoesNotExist:
                messages.error(request, 'Invalid top-up code.')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {e}')

    else:
        form = TopUpCodeForm()

    return render(request, 'core/top_up.html', {'form': form})

@login_required
def top_ups(request):
    top_ups_list = TopUpTransaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'core/top_ups.html', {'top_ups_list': top_ups_list})

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def top_ups_admin(request):
    applied_top_ups = TopUpTransaction.objects.filter(top_up_code__is_used=True).order_by('-timestamp')
    available_top_ups = TopUpCode.objects.filter(is_used=False).order_by('exp_date')

    return render(request, 'core/top_ups_admin.html', {
        'applied_top_ups': applied_top_ups,
        'available_top_ups': available_top_ups,
    })
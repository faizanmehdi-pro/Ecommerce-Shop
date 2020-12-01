from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *


def index(request):
    context = {}
    return render(request, 'shop/shop.html', context)


@login_required(login_url='login')
def shop(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/shop.html', context)


@login_required(login_url='login')
def cart(request):
    # Authenticating the user
    if request.user.is_authenticated:
        # Getting customer using OneToOne Relationship
        customer = request.user.customer
        # Getting the order object if not then creating it
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Looking up in the orderitems
        # parent.child_set (All in lower-case). It is a way to look into child
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, 'shop/cart.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print("ID is: ", productId)
    print("Action is: ", action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item is added", safe=False)


@login_required(login_url='login')
def placeorder(request):
    template = render_to_string('shop/email_template.html', {'name': request.user.customer.name})
    customer_email = request.user.customer.email
    send_mail(
        'Order Placed',
        template,
        'settings.EMAIL_HOST_USER',
        [customer_email, 'faizanmehdi572@gmail.com'],
    )
    return redirect('shop')
    context = {}
    return render(request, 'shop/shop.html', context)


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('shop')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('shop')

        context = {'form': form}
        return render(request, 'account/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('shop')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('shop')
        else:
            messages.info(request, 'Username and Password is incorrect')
    context = {}
    return render(request, 'account/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

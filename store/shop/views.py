from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
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


# Restricting the users access
@login_required(login_url='login')
def shop(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/shop.html', context)


@login_required(login_url='login')
def cart(request):
    # Authenticating the user
    if request.user.is_authenticated:
        user = request.user
        # Getting the order object if not then creating it
        order, created = Order.objects.get_or_create(user=user, complete=False)
        # Looking up in the orderitems
        # parent.child_set (All in lower-case). It is a way to look into child
        items = order.orderitem_set.all()

    context = {'items': items, 'order': order}
    return render(request, 'shop/cart.html', context)


def updateItem(request):
    # Getting json data from fetch API
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    # Getting user
    user = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(user=user, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Adding the items will increase the orderItem quantity
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item is added", safe=False)


@login_required(login_url='login')
def placeorder(request):
    # Making the template
    template = render_to_string('shop/email_template.html')
    # Getting user email
    user_email = request.user.email
    # Django send_email (For sending email to user and Admin mail accounts)
    send_mail(
        'Order Placed',
        template,
        'settings.EMAIL_HOST_USER',
        [user_email, 'EMAIL_HOST_USER'],
    )
    return redirect('shop')
    context = {}
    return render(request, 'shop/shop.html', context)


def registerPage(request):
    # If already a user than redirect to shop page.
    if request.user.is_authenticated:
        return redirect('shop')
    else:
        # Using CreateUserForm from forms.py
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            # Validating
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

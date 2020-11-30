from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .models import *


def index(request):
    context = {}
    return render(request, 'shop/shop.html', context)


def shop(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/shop.html', context)


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


def checkout(request):
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'shop/checkout.html', context)


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


def placeorder(request, uid):
    template = render_to_string('shop/email_template', {'name': request.user.customer.name})

    email = EmailMessage(
        'Thank you for placing the order',
        template,
        settings.EMAIL_HOST_USER,
        [request.user.customer.email],
        )

    email.fail.silently = False
    email.send()

    return redirect('shop')
    context = {'customer': customer}

    return render(request, 'shop/shop.html', context)
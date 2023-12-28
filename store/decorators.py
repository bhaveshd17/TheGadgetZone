from django.shortcuts import redirect
from django.http import HttpResponse

from store.models import Order


def unauthenticated_user(view_function):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return view_function(request, *args, **kwargs)

    return wrapper_function

def allowed_users(allowed_roles=[]):
    def decorator(view_function):
        def wrapper_function(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                print(group)
            if group in allowed_roles:
                 return view_function(request, *args, **kwargs)
            else:
                return HttpResponse('You are not authorized to view this page')

        return wrapper_function
    return decorator

def allowed_admin(view_function):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'customer':
            return redirect('/')

        if group == 'admin':
             return view_function(request, *args, **kwargs)
        else:
            return HttpResponse('You are not authorized to view thi page')

    return wrapper_function


def allowed_checkout(view_function):
    def wrapper_function(request, *args, **kwargs):
        customer = request.user.customer
        order = Order.objects.filter(customer=customer).order_by('-id')[0:1].get()
        if order.get_cart_total == 0 and order.get_cart_items == 0:
            return HttpResponse('You have not added item to cart yet')
        else:
            return view_function(request, *args, **kwargs)

    return wrapper_function


import json
from math import ceil

from .models import *

def cookiesCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    # print(cart)

    items = []
    order = {'get_cart_total': 0,'get_original_cart_total':0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_total']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.discountPrice * cart[i]['quantity'])
            originalTotal = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_original_cart_total'] += originalTotal
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'category':product.category,
                    # 'subCategory':product.subCategory,
                    'savePrice':product.savePrice,
                    'price': product.price,
                    'discountPrice':product.discountPrice,
                    'ImageUrl': product.ImageUrl,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
                'get_original_total':originalTotal,
            }
            items.append(item)
            # print(items)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    return {'cartItems':cartItems, 'order':order, 'items':items, 'save': order['get_original_cart_total'] - order['get_cart_total']}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        save = order.get_original_cart_total - order.get_cart_total
    # print('created order', created)
    else:
        cookiesData = cookiesCart(request)
        items = cookiesData['items']
        order = cookiesData['order']
        cartItems = cookiesData['cartItems']
        save = cookiesData['save']


    return {'cartItems':cartItems, 'order':order, 'items':items, 'save': save}

def showProductsData(request):
    categories = Category.objects.all()
    cat_id = request.GET.get('category')
    if cat_id:
        products = Product.objects.filter(category=cat_id)
        cat_name = Category.objects.get(id=cat_id)
    else:
        products = Product.objects.all()
        cat_name = "All"
    return {'products': products, 'categories': categories, 'cat_name': cat_name}

def productFormData(request):
    product = Product()
    product.name = request.POST.get('name')
    price = float(request.POST.get('price'))
    rate = int(request.POST.get('rate'))
    savePrice = ceil((price * rate) / 100)
    discountPrice = price - savePrice
    product.price = price
    product.rate = rate
    product.savePrice = savePrice
    product.description = request.POST.get('description')
    product.discountPrice = discountPrice
    categoryId = request.POST.get('category')
    product.category = Category.objects.get(id=categoryId)
    product.digital = request.POST.get('digital')
    product.image = request.FILES.get('image')
    return product
# def guestOrder(request, data):
#     print('User is not logged in')
#     print('cookies', request.COOKIES)
#     name = data['form']['name']
#     email = data['form']['email']
#     cookiesData = cookiesCart(request)
#     items = cookiesData['items']
#
#     customer, created = Customer.objects.get_or_create(
#         email=email,
#     )
#     customer.name = name
#     customer.save()
#
#     order = Order.objects.create(
#         customer=customer,
#         complete=False
#     )
#
#     for item in items:
#         product = Product.objects.get(id=item['product']['id'])
#         orderItem = OrderItem.objects.create(
#             product=product,
#             order=order,
#             quantity=item['quantity']
#         )
#
#     return customer, order


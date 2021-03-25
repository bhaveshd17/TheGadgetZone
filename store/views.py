import datetime
import json
from math import ceil

from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from .utils import cartData, guestOrder


def store(request):

	data = cartData(request)
	cartItems = data['cartItems']

	# products = Product.objects.all()
	categoryOfProducts = Product.objects.values('category', 'id')
	allProducts = []
	categories = [item['category'] for item in categoryOfProducts]
	categoriesC = set(categories)
	for category in categoriesC:
		products = Product.objects.filter(category=category)
		n = len(products)
		nSlide = n // 4 + ceil((n / 4) - (n // 4))
		allProducts.append([products, range(1, nSlide), nSlide])

	content = {'allProducts':allProducts, 'cartItems':cartItems}
	return render(request, 'store/store.html', content)

def cart(request):

	data = cartData(request)
	items = data['items']
	order = data['order']
	cartItems = data['cartItems']

	content = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', content)

def checkout(request):

	data = cartData(request)
	items = data['items']
	order = data['order']
	cartItems = data['cartItems']

	content = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', content)



def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	# print(productId, action)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
	if action == 'add':
		orderItem.quantity = (orderItem.quantity+1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity-1)
	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('item added', safe=False)


def processOrder(request):
	# print(request.body)
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)


	else:
		customer, order = guestOrder(request, data)


	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()
	if order.shipping == True:
		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
			country=data['shipping']['country']
		)

	return JsonResponse('Payment Complete', safe=False)


def dashboard(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orderItems = OrderItem.objects.all().order_by("date")
	customers = Customer.objects.all()
	total_order = orderItems.count()
	order = []
	for orderItem in orderItems:
		order.append(orderItem.order.status)

	delivered = order.count('Delivered')
	pending = order.count('Pending')

	content={
		'cartItems':cartItems,
		'customers':customers,
		'orderItems':[orderItems[i] for i in range(0, 5)],
		'total_order':total_order,
		'delivered':delivered,
		'pending':pending
	}
	return render(request, 'store/dashboard.html', content)

def allOrders(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orderItems = OrderItem.objects.all().order_by("date")
	customers = Customer.objects.all()
	content = {
		'cartItems': cartItems,
		'customers': customers,
		'orderItems': orderItems,
	}
	return render(request, 'store/allOrders.html', content)
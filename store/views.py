import datetime
import json
from math import ceil
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from .utils import cartData, guestOrder
from .form import AddProductForm

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


	# allProducts = [[products, nSlide, range(1, nSlide)], [products, nSlide, range(1, nSlide)]]
	content = {'allProducts':allProducts, 'cartItems':cartItems}

	# for p in product:
	# 	print(p.image.url)
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
	customers = Customer.objects.all()
	orderItem = OrderItem.objects.all().order_by("-date")
	orderItems = [orderItem[i] for i in range(0, 5)]
	delivered = orderItem.filter(status='Delivered').count()
	pending = orderItem.filter(status='Pending').count()
	content = {
		'cartItems':cartItems,
		'customers':customers,
		'orderItems':orderItems,
		'total_order':orderItem.count(),
		'delivered':delivered,
		'pending':pending,


	}
	return render(request, 'store/dashboard.html', content)

def allOrder(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orderItems = OrderItem.objects.all().order_by("-date")
	content = {'cartItems':cartItems, 'orderItems':orderItems}
	return render(request, 'store/allOrder.html', content)

def addProducts(request):
	data = cartData(request)
	cartItems = data['cartItems']
	categories = Category.objects.all()
	if request.method == 'POST':
		product = Product()
		product.name = request.POST.get('name')
		price = float(request.POST.get('price'))
		rate = int(request.POST.get('rate'))
		savePrice = ceil((price*rate)/100)
		discountPrice = price - savePrice
		product.price = price
		product.rate = rate
		product.savePrice = savePrice
		product.discountPrice = discountPrice
		categoryId = request.POST.get('category')
		product.category = Category.objects.get(id=categoryId)
		product.digital = request.POST.get('digital')
		product.image = request.FILES.get('image')
		product.save()
		return redirect('/')

	content = {'cartItems':cartItems, 'categories':categories}
	return render(request, 'store/product_form.html', content)
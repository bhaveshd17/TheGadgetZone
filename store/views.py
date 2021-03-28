import datetime
import json
from math import ceil
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from .utils import cartData, guestOrder
from django.contrib.auth.hashers import make_password, check_password

def store(request):

	data = cartData(request)
	cartItems = data['cartItems']

	categoryOfProducts = Product.objects.values('category', 'id')
	allProducts = []
	categories = [item['category'] for item in categoryOfProducts]
	categoriesC = set(categories)
	for category in categoriesC:
		products = Product.objects.filter(category=category)
		n = len(products)
		nSlide = n // 3 + ceil((n / 3) - (n // 3))
		allProducts.append([products, range(1, nSlide), nSlide])


	content = {
		'allProducts': allProducts,
		'cartItems': cartItems,
		'categories':Category.objects.all(),

	}
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
	shipping = orderItem.filter(status='Shipping').count()
	accepted = orderItem.filter(status='Accepted').count()
	content = {
		'cartItems':cartItems,
		'customers':customers,
		'orderItems':orderItems,
		'total_order':orderItem.count(),
		'delivered':delivered,
		'pending':pending,
		'accepted': accepted,
		'shipping': shipping,

	}
	return render(request, 'admin/dashboard.html', content)

def allOrder(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orderItems = OrderItem.objects.all().order_by("-date")
	content = {'cartItems':cartItems, 'orderItems':orderItems}
	return render(request, 'admin/allOrder.html', content)

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
	return render(request, 'admin/product_form.html', content)

def addCategory(request):
	if request.method == 'POST':
		category = request.POST.get('category')
		return redirect('/')

	return redirect('/')



def acceptBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("acceptOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		if orderItem.status == "Pending":
			orderItem.status = "Accepted"
			orderItem.save()
		else:
			print('message already accepted')
		return redirect('/dashboard/allOrder')
	else:
		return redirect('/dashboard/allOrder')

def shippingBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("shippingOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		print(orderItem)
		if orderItem.status == "Accepted":
			orderItem.status = "Shipping"
			orderItem.save()
		else:
			print('message already Shipped')
		return redirect('/dashboard/allOrder')
	else:
		return redirect('/dashboard/allOrder')

def deliveredBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("deliveredOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		if orderItem.status == "Shipping":
			orderItem.status = "Delivered"
			orderItem.save()
		else:
			print('message already Delivered')
		return redirect('/dashboard/allOrder')
	else:
		return redirect('/dashboard/allOrder')

def removeOrderBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("removeOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		orderItem.delete()
		return redirect('/dashboard/allOrder')

	else:
		return redirect('/dashboard/allOrder')

def orderDelivered(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orderItems = OrderItem.objects.filter(status="Delivered")
	content = {'cartItems':cartItems, 'orderItems':orderItems}
	return render(request, 'admin/deliveredOrder.html', content)

def showProducts(request):
	data = cartData(request)
	cartItems = data['cartItems']
	categories = Category.objects.all()
	cat_id = request.GET.get('category')
	if cat_id:
		products = Product.objects.filter(category=cat_id)
		cat_name = Category.objects.get(id=cat_id)
	else:
		products = Product.objects.all()
		cat_name = "All"
	content = {
		'cartItems': cartItems,
		'products':products,
		'categories':categories,
		'cat_name':cat_name
	}
	return render(request, 'store/showProducts.html', content)

def login(request):
	if request.method == 'GET':
		return render(request, 'authentication/login.html')

	else:
		email = request.POST.get('email')
		password = request.POST.get('password')
		customer = Customer.get_user_by_email(email)

		print(email, password)

		error_message = None
		if customer:
			flag = check_password(password, customer.password)
			if flag:
				return redirect("store")
			else:
				error_message = "Email or Password Does not Exist"
		else:
			error_message = "Email or Password Does not exist"
		return render(request, 'authentication/login.html', {'error' : error_message})


def signup(request):
	if request.method == 'GET':
		return render(request, 'authentication/signup.html')
	else:
		postData = request.POST
		name = postData.get('name')
		email = postData.get('email')
		phone = postData.get('phone')
		password = postData.get('password')
		conf_password = postData.get('conf_password')
		# validation
		value = {
			'name': name,
			'email': email,
			'phone': phone,
		}

		error_message = None

		user = Customer(name= name,
					 email=email,
					 phone=phone,
					 password=password,
					 conf_password=conf_password)

		if (not email):
			error_message = "Email is Required..!"
		elif (not name):
			error_message = "Name is required..!"
		elif not phone:
			error_message = "Phone Number Required..!"
		elif len(phone) < 10:
			error_message="Phone Number must be 10 digit long"
		elif len(password)<6:
			error_message = "Password must be more than 6 character"
		elif conf_password != password:
			error_message = "Password is not same..! please try again"
		elif user.isExists():
			error_message = 'Email ID is already register ! Go to login page'

	if not error_message:
		user.password= make_password(user.password)
		user.conf_password = make_password(user.conf_password)
		user.register()
		return redirect("store")

	else:
		data = {
				'error': error_message,
				'values': value
			}
		return render(request, 'authentication/signup.html', data)


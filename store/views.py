import datetime
import json
from math import ceil
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.http import JsonResponse
from .utils import cartData, showProductsData
from django.contrib import messages
from .form import UserCreationForm, CustomerForm
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users


@unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			messages.success(request, f"{user} logged in successfully")
			login(request, user)
			return redirect('/')
		else:
			messages.error(request, 'Wrong username or password')
			return render(request, 'authentication/login.html')

	return render(request, 'authentication/login.html')


@unauthenticated_user
def signup(request):
	form = UserCreationForm()
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')

			login(request, user)
			messages.success(request, f"Account for {username} created successfully")
			return redirect('/')
	content = {'form': form}
	return render(request, 'authentication/signup.html', content)

def logoutUser(request):
	logout(request)
	messages.success(request, 'Good Bye')
	return redirect('/')





@login_required(login_url='login')
def userPage(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orders = request.user.customer.order_set.all()
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES, instance=customer)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully update information")
			return redirect('/')
	address = UserAddress.objects.filter(customer=customer)
	content = {

		'orders': orders,
		'cartItems':cartItems,
		'form':form,
		'address':address
	}
	return render(request, 'store/userPage.html', content)

@login_required(login_url='login')
def userOrderDetails(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = Order.objects.filter(customer=request.user.customer)
	order_list=[]
	for i in order:
		orderItem = OrderItem.objects.filter(order=i)
		order_list.append(orderItem)

	content = {'cartItems': cartItems, 'order_list':order_list}
	return render(request, 'store/userOrderDetails.html', content)


@login_required(login_url='login')
def addAddress(request):
	userAddress = UserAddress()
	userAddress.address = request.POST.get('address')
	userAddress.city = request.POST.get('city')
	userAddress.state = request.POST.get('state')
	userAddress.zipcode = request.POST.get('zipcode')
	userAddress.country = request.POST.get('country')
	userAddress.customer = request.user.customer
	userAddress.save()
	messages.success(request, 'Address added successfully')
	return redirect('/userPage')


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

def search(request):
	data = cartData(request)
	productData = showProductsData(request)
	cartItems = data['cartItems']
	categories = productData['categories']
	cat_name = productData['cat_name']
	query = request.GET['query']
	if len(query)>78:
		products = Product.objects.none()
	else:
		products = Product.objects.filter(name__icontains=query)
		# productDesc = Product.objects.filter(description=query)
		# products = productsName.union(productDesc)
	content = {
		'cartItems': cartItems,
		'products':products,
		'categories':categories,
		'cat_name':cat_name,
		'query':query
	}

	return render(request, 'store/search.html', content)
def showProducts(request):
	data = cartData(request)
	productData = showProductsData(request)
	cartItems = data['cartItems']
	products = productData['products']
	categories = productData['categories']
	cat_name = productData['cat_name']
	content = {
		'cartItems': cartItems,
		'products':products,
		'categories':categories,
		'cat_name':cat_name
	}
	return render(request, 'store/showProducts.html', content)


def cart(request):

	data = cartData(request)
	items = data['items']
	order = data['order']
	cartItems = data['cartItems']
	save = data['save']

	content = {
		'items': items,
		'order': order,
		'cartItems': cartItems,
		'save':save,
	}
	return render(request, 'store/cart.html', content)

@login_required(login_url='login')
def checkout(request):

	data = cartData(request)
	items = data['items']
	order = data['order']
	cartItems = data['cartItems']
	customer = request.user.customer
	address = UserAddress.objects.filter(customer=customer)

	content = {'items':items, 'order':order, 'cartItems':cartItems, 'address':address}
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

@login_required(login_url='login')
def processOrder(request):
	# # print(request.body)
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)


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






# admin pages
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
	data = cartData(request)
	cartItems = data['cartItems']
	customers = Customer.objects.all()
	orderItem = OrderItem.objects.all().order_by("-date")
	if len(orderItem)>=5 :
		orderItems = [orderItem[i] for i in range(0, 5)]
	else:
		orderItems = [orderItem[i] for i in range(0, len(orderItem))]
	if len(customers)>=5:
		customers = [customers[i] for i in range(1, 6)]
	else:
		customers = [customers[i] for i in range(0, len(customers))]
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def allOrder(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orderItems = OrderItem.objects.all().order_by("-date")
	content = {'cartItems':cartItems, 'orderItems':orderItems}
	return render(request, 'admin/allOrder.html', content)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
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
		messages.success(request, f"Successfully added {product}")
		return redirect('/')

	content = {'cartItems':cartItems, 'categories':categories}
	return render(request, 'admin/product_form.html', content)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def addCategory(request):
	if request.method == 'POST':
		category = request.POST.get('category')
		return redirect('/')

	return redirect('/')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def acceptBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("acceptOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		if orderItem.status == "Pending":
			orderItem.status = "Accepted"
			messages.success(request, f"{orderItem} Order Accepted")
			orderItem.save()
		else:
			messages.warning(request, f"{orderItem} Order already Accepted")
		return redirect('/dashboard/allOrder')
	else:
		return redirect('/dashboard/allOrder')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def shippingBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("shippingOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		print(orderItem)
		if orderItem.status == "Accepted":
			orderItem.status = "Shipping"
			orderItem.save()
			messages.success(request, f"{orderItem} Send for shipment !")
		else:
			messages.warning(request, f"{orderItem} already Shipped")
		return redirect('/dashboard/allOrder')
	else:
		return redirect('/dashboard/allOrder')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deliveredBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("deliveredOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		if orderItem.status == "Shipping":
			orderItem.status = "Delivered"
			orderItem.save()
			messages.success(request, f"{orderItem} successfully delivered !")
		else:
			messages.warning(request, f"{orderItem} already Delivered")
		return redirect('/dashboard/allOrder')
	else:
		return redirect('/dashboard/allOrder')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def removeOrderBtn(request):
	if request.method == 'POST':
		order_id = request.POST.get("removeOrder")
		orderItem = OrderItem.objects.get(id=order_id)
		orderItem.delete()
		messages.success(request, f"{orderItem} remove successfully !")
		return redirect('/dashboard/allOrder')

	else:
		return redirect('/dashboard/allOrder')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def orderDelivered(request):
	data = cartData(request)
	cartItems = data['cartItems']
	orderItems = OrderItem.objects.filter(status="Delivered")
	content = {'cartItems':cartItems, 'orderItems':orderItems}
	return render(request, 'admin/deliveredOrder.html', content)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def allCustomers(request):
	data = cartData(request)
	cartItems = data['cartItems']
	customers = Customer.objects.all()

	content = {'cartItems': cartItems,'customers':customers}
	return render(request, 'admin/allCustomers.html', content)

@login_required(login_url='login')
def remove_customer(request, pk):
	customer = Customer.objects.get(id=pk)
	username = customer.user.username
	user = User.objects.get(username=username)
	customer.delete()
	user.delete()
	messages.success(request, f"Successfully delete {username}'s account from the gadgets zone!")
	return redirect('/dashboard/allCustomers')

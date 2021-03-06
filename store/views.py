import random
from datetime import datetime, timedelta
import json
from math import ceil
import cloudinary.uploader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, HttpResponse

from .dashboard import dashboardContent
from .models import *
from django.http import JsonResponse

from .send_email import sendMail, otpMail
from .utils import cartData, showProductsData, productFormData, cookiesCart, getting_email
from django.contrib import messages
from .form import UserCreationForm, CustomerForm, ProductForm
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, allowed_checkout


@unauthenticated_user
def loginPage(request):
	print(request.COOKIES)
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, f"{user} logged in successfully")
			return redirect('/')
		else:
			messages.error(request, 'Wrong username or password')
			return render(request, 'authentication/login.html')

	return render(request, 'authentication/login.html')


@unauthenticated_user
def signup(request):
	# form = UserCreationForm()
	if request.method == 'POST':
		get_otp = request.POST.get('otp')
		# form = UserCreationForm(request.POST)

		if get_otp:
			get_user = request.POST.get('user')
			user = User.objects.get(username=get_user)
			try:
				if int(get_otp) == UserOTP.objects.filter(user=user).last().otp:
					user.is_active = True
					user.save()
					messages.success(request, f'Account is Created for {user.username}')
					sendMail(request, [user.email], {
						'head': 'accountCreated',
						'p1': 'WELCOME',
						'p2': user.username,
						'p3': 'Thanks for signing up to The Gadget Zone store. Enjoy Electronics Shopping in Gadget Zone store. Click below link for continue shopping.',
					}, 'AddPAndWelcome', 'Welcome To The Gadget Zone')
					return redirect('/')
				else:
					messages.warning(request, f'OTP is Inavalid')
					return render(request, 'authentication/signup.html', {'otp': True, 'user': user})

			except:
				messages.warning(request, f'OTP is Inavalid')
				return render(request, 'authentication/signup.html', {'otp': True, 'user': user})

		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			user = User.objects.get(username=username)
			user.email = email
			user.username = username
			user.is_active = False
			user.save()
			user_otp = random.randint(100000, 999999)
			messages.success(request, f"OTP send to {user.email}")
			UserOTP.objects.create(user=user, otp=user_otp)
			otpMail(request, user.email, username, user_otp)
			login(request, user)
			return render(request, 'authentication/signup.html', {'otp': True, 'user': user})
	else:
		form = UserCreationForm()

	content = {'form': form}
	return render(request, 'authentication/signup.html', content)

@unauthenticated_user
def resend_otp(request):
	if request.method == "GET":
		get_user = request.GET.get('user')
		if User.objects.filter(username=get_user).exists() and not User.objects.get(username=get_user).is_active:
			user = User.objects.get(username=get_user)
			user_otp = random.randint(100000, 999999)
			UserOTP.objects.create(user=user, otp=user_otp)
			otpMail(request, user.email, user.username, user_otp)
			return HttpResponse("Re Send")

	return HttpResponse("Can't Send")


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
	user = User.objects.get(customer=customer)
	form = CustomerForm(instance=customer)
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES, instance=customer)
		email = request.POST.get('email')
		if form.is_valid():
			form.save()
			user.email = email
			user.save()
			messages.success(request, "Successfully update information")
			return redirect('/')
	address = UserAddress.objects.filter(customer=customer)
	content = {

		'orders': orders,
		'cartItems':cartItems,
		'customer':customer,
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
def cancelOrder(request, pk):
	orderItem = OrderItem.objects.get(id=pk)
	orderItem.delete()
	messages.success(request, f"Order for {orderItem} Successfully Canceled")
	return redirect('/userOrderDetails')

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
	if '/userPage/' in request.META.get('HTTP_REFERER'):
		return redirect('/userPage')
	else:
		return redirect('/checkout')

@login_required(login_url='login')
def remove_address(request, pk):
	address = UserAddress.objects.get(id=pk)
	address.delete()
	messages.success(request, 'Address removed successfully')
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
	if request.COOKIES and request.user.is_authenticated:
		customer = request.user.customer
		order = Order.objects.filter(customer=customer).order_by('-id')[0:1].get()
		cookiesData = cookiesCart(request)
		itemsCookie = cookiesData['items']
		for item in itemsCookie:
			product = Product.objects.get(id=item['product']['id'])
			OrderItem.objects.create(
				product=product,
				order=order,
				quantity=item['quantity']
			)
		response = render(request, 'store/store.html', content)
		response.delete_cookie('cart')
		return response

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
		productsName = Product.objects.filter(name__icontains=query)
		productTag = Product.objects.filter(tags__icontains=query)
		products = productTag.union(productsName)
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

def viewProducts(request, pk):
	data = cartData(request)
	cartItems = data['cartItems']
	product = Product.objects.get(id=pk)
	date = (datetime.now()+ timedelta(days=6)).strftime('%d %A')
	reviews = Review.objects.filter(product=product)
	content = {
		'cartItems': cartItems,
		'product':product,
		'reviews':reviews,
		'date':date,
		'range':range(1, 6)
	}
	return render(request, 'store/viewProducts.html', content)

@login_required(login_url='login')
def reviewProduct(request, pk):
	rating = request.POST.get('rating')
	body = request.POST.get('body')
	product = Product.objects.get(id=pk)
	customer = request.user.customer
	review = Review(
		rating=rating,
		body=body,
		product=product,
		customer=customer
	)
	review.save()
	return redirect(f'/viewProducts/{pk}')
@login_required(login_url='login')
def delete_review(request, pk, rk):
	review = Review.objects.get(id=rk)
	review.delete()
	messages.success(request, "review deleted successfully")
	return redirect(f'/viewProducts/{pk}')

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
@allowed_checkout
def checkout(request):

	data = cartData(request)
	items = data['items']
	order = data['order']
	cartItems = data['cartItems']
	customer = request.user.customer
	address = UserAddress.objects.filter(customer=customer)
	content = {'items':items, 'order':order, 'cartItems':cartItems, 'address':address}
	return render(request, 'store/checkout.html', content)

@login_required(login_url='login')
def thankYou(request):
	data = cartData(request)
	cartItems = data['cartItems']
	content = {'cartItems':cartItems}
	return render(request, 'store/thankyou.html', content)


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
	transaction_id = datetime.now().timestamp()
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
	sendMail(request, [request.user.email], {
		'username':request.user.username,
		'products':OrderItem.objects.filter(order=order),
		'order':order,
		'msg':'Confirmed'
	}, 'delivery', 'order confirmation mail')
	return JsonResponse('Payment Complete', safe=False)






# admin pages
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
	content = dashboardContent(request)
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
		product = productFormData(request)
		product.save()
		p_id = product.id
		sendMail(request, getting_email(), {
			'head': 'ProductAdded',
			'p2':f'Hey! New Product added to gadgets Zone',
			'img':Product.objects.get(id=p_id).ImageUrl,
			'p3':f'{product.name}',
			'p4':f'Price : {product.discountPrice}',
			'p5':'Grab the offer hurry up before out !!',

		}, 'AddPAndWelcome', 'New product out!!')
		messages.success(request, f"Successfully added {product}")
		return redirect('/')

	content = {'cartItems':cartItems, 'categories':categories}
	return render(request, 'admin/product_form.html', content)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def addCategory(request):
	if request.method == 'POST':
		category = request.POST.get('category')
		categoryCreate = Category(category=category)
		categoryCreate.save()
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
		if orderItem.status == "Accepted":
			orderItem.status = "Shipping"
			orderItem.save()
			oid = orderItem.order.id
			order = Order.objects.get(id=oid)
			sendMail(request, [order.customer.email], {
				'username': order.customer.user.username,
				'products': orderItem,
				'order': order,
				'msg': 'Shipped'
			}, 'delivery', 'order status details')
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
			oid = orderItem.order.id
			order = Order.objects.get(id=oid)
			sendMail(request, [order.customer.email], {
				'username': order.customer.user.username,
				'products': orderItem,
				'order': order,
				'msg': 'Delivered'
			}, 'delivery', 'order status details')
			messages.success(request, f"{orderItem} successfully delivered !")
		else:
			messages.warning(request, f"{orderItem} already Delivered")

		return redirect('/dashboard/allOrder')
	else:
		return redirect('/dashboard/allOrder')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def allCustomers(request):
	data = cartData(request)
	cartItems = data['cartItems']
	customers = Customer.objects.all()
	flag = True
	if request.GET.get('searchUsername'):
		query = request.GET.get('searchUsername')
		try:
			user = User.objects.get(username=query)
		except:
			user = User.objects.none()
		if user:
			customers = Customer.objects.filter(user=user)
		else:
			flag = False

	content = {'cartItems': cartItems,'customers':customers, 'flag':flag}
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

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def remove_product(request, pk):
	product = Product.objects.get(id=pk)
	try:
		orderItem = OrderItem.objects.get(product=product)
	except:
		orderItem = OrderItem.objects.none()
	cloudinary.uploader.destroy(product.image.public_id,invalidate=True)
	orderItem.delete()
	product.delete()
	messages.success(request, f"successfully delete product {product}")
	return redirect('/')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def edit_product(request, pk):
	data = cartData(request)
	cartItems = data['cartItems']
	product = Product.objects.get(id=pk)
	form = ProductForm(instance=product)
	p_id = product.image.public_id
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			form.save()
			if p_id != product.image.public_id:
				cloudinary.uploader.destroy(p_id, invalidate=True)
			messages.success(request, "Product update successfully")
			return redirect(f'/viewProducts/{pk}')
	content = {'cartItems':cartItems, 'form':form}
	return render(request, 'admin/edit_product_form.html', content)
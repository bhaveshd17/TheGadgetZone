from datetime import datetime, timedelta
import json
from math import ceil
import cloudinary.uploader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.http import JsonResponse

from .send_email import sendMail
from .utils import cartData, showProductsData, productFormData, cookiesCart
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
	form = UserCreationForm()
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			login(request, user)
			messages.success(request, f"Account for {username} created successfully")
			sendMail(request, email)
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
		productDesc = Product.objects.filter(description=query)
		products = productDesc.union(productsName)
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
		product = productFormData(request)
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
			cloudinary.uploader.destroy(p_id, invalidate=True)
			form.save()
			messages.success(request, "Product update successfully")
			return redirect(f'/viewProducts/{pk}')
	content = {'cartItems':cartItems, 'form':form}
	return render(request, 'admin/edit_product_form.html', content)
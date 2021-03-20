import datetime
import json

from django.shortcuts import render
from .models import *
from django.http import JsonResponse

def store(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
		cartItems = []


	product = Product.objects.all()
	content = {'products':product, 'cartItems':cartItems}

	# for p in product:
	# 	print(p.image.url)
	return render(request, 'store/store.html', content)

def cart(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
		# print('created order', created)
	else:
		try:
			cart = json.loads(request.COOKIES['cart'])
		except:
			cart = {}
		# print(cart)

		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
		cartItems = order['get_cart_total']

		for i in cart:
			try:
				cartItems += cart[i]['quantity']
				product = Product.objects.get(id=i)
				total = (product.price * cart[i]['quantity'])
				order['get_cart_total'] += total
				order['get_cart_items'] += cart[i]['quantity']

				item = {
					'product': {
						'id': product.id,
						'name': product.name,
						'price': product.price,
						'ImageUrl': product.ImageUrl,
					},
					'quantity': cart[i]['quantity'],
					'get_total': total
				}
				items.append(item)
				# print(items)
				if product.digital == False:
					order['shipping'] = True
			except:
				pass


	content = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', content)

def checkout(request):
	# if request.method == 'POST':
	# 	print(request.POST)
	# 	if request.user.is_authenticated:
	# 		address = request.POST.get('address')
	# 		city = request.POST.get('city')
	# 		state = request.POST.get('state')
	# 		zipcode = request.POST.get('zipcode')
	# 		country = request.POST.get('country')
	# 		print('hello')
	# 		shippingAddress = ShippingAddress(address=address, city=city, state=state, zipcode = zipcode, country=country)
	# 		shippingAddress.save()


	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
		cartItems = []

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
		total = float(data['form']['total'])
		order.transaction_id = transaction_id
		
		if total == order.get_cart_total:
			order.complete = True
		order.save()
		if order.shipping == True:
			ShippingAddress.objects.create(
				customer = customer,
				order = order,
				address = data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
				country=data['shipping']['country']
			)

	else:
		print('User is not logged in')

	return JsonResponse('Payment Complete', safe=False)
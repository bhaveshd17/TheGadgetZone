from django.urls import path
from . import views

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path('showProducts/', views.showProducts, name="showProducts"),

	path('dashboard/', views.dashboard, name="dashboard"),
	path('dashboard/allOrder/', views.allOrder, name="allOrder"),
	path('addProducts/', views.addProducts, name="addProducts"),
	path('addProducts/addCategory', views.addCategory, name="addCategory"),
	path('dashboard/allOrder/accept', views.acceptBtn, name="accept"),
	path('dashboard/allOrder/shipping', views.shippingBtn, name="shipping"),
	path('dashboard/allOrder/delivered', views.deliveredBtn, name="delivered"),
	path('dashboard/allOrder/remove', views.removeOrderBtn, name="remove"),
	path('dashboard/orderDelivered', views.orderDelivered, name="orderDelivered"),

	path('login/', views.login, name="login"),
	path('signup/', views.signup, name="signup"),

]
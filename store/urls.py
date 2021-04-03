from django.urls import path
from . import views

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('transactionCompleted/', views.thankYou, name="transactionCompleted"),
    path('update_item/', views.updateItem, name="update_item"),
	path('viewProducts/<int:pk>/', views.viewProducts, name="viewProducts"),
	path('viewProducts/<int:pk>/reviewProduct/', views.reviewProduct, name="reviewProduct"),
	path('viewProducts/<int:pk>/delete_review/<int:rk>/', views.delete_review, name="delete_review"),
	path('process_order/', views.processOrder, name="process_order"),
	path('showProducts/', views.showProducts, name="showProducts"),
	path('userPage/', views.userPage, name="userPage"),
	path('addAddress/', views.addAddress, name="addAddress"),
	path('remove_address/<int:pk>',views.remove_address, name="remove_address"),
	path('userOrderDetails/', views.userOrderDetails, name="userOrderDetails"),
	path('cancelOrder/<int:pk>/', views.cancelOrder, name="cancelOrder"),
	path('search/', views.search, name='search'),

	path('remove_product/<int:pk>/', views.remove_product, name="remove_product"),
	path('edit_product/<int:pk>', views.edit_product, name="edit_product"),
	path('dashboard/', views.dashboard, name="dashboard"),
	path('dashboard/allOrder/', views.allOrder, name="allOrder"),
	path('addProducts/', views.addProducts, name="addProducts"),
	path('addProducts/addCategory', views.addCategory, name="addCategory"),
	path('dashboard/allOrder/accept', views.acceptBtn, name="accept"),
	path('dashboard/allOrder/shipping', views.shippingBtn, name="shipping"),
	path('dashboard/allOrder/delivered', views.deliveredBtn, name="delivered"),
	path('dashboard/orderDelivered', views.orderDelivered, name="orderDelivered"),
	path('dashboard/allCustomers', views.allCustomers, name='allCustomers'),
	path('dashboard/allCustomers/<int:pk>/', views.remove_customer, name='remove_customer'),

	path('login/', views.loginPage, name="login"),
	path('signup/', views.signup, name="signup"),
	path('logout/', views.logoutUser, name="logout"),

]
from django.urls import path
from . import views

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path('dashboard/', views.dashboard, name="dashboard"),
	path('dashboard/allOrder/', views.allOrder, name="allOrder"),
	path('addProducts/', views.addProducts, name="addProducts"),

]
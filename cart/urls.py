from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<product_id>/', views.cart_add, name='cart_add'),
    path('remove/<product_id>/', views.cart_remove, name='cart_remove'),
    path('remove_all/<products_id>', views.remove_all, name='remove_all'),
    path('order/final', views.order, name='order'),
    path('order/final/<str:retail>', views.order, name='order-retail'),
    path('order/final/index/seaching', views.delivery, name='order-index'),
    path('order/final/payment/', views.payment, name='payment'),
    path('order/final/payment/<int:delivery_type>/', views.payment, name='payment-auto'),

]
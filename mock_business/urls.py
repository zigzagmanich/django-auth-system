from django.urls import path
from mock_business import views

app_name = 'mock_business'

urlpatterns = [
    path('products/', views.products_list_view, name='products_list'),
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    
    path('orders/', views.orders_list_view, name='orders_list'),
    path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),
]
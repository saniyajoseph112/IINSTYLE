from django.urls import path
from .import views
app_name='cart'

urlpatterns = [
    path('cart/',views.cart,name='cart'),
    path('add_to_cart/',views.add_to_cart,name='add_to_cart'),
    path('update_cart_quantity/',views.update_cart_quantity,name='update_cart_quantity'),
    path('remove_item_cart/<int:pk>/',views.remove_item_cart,name='remove_item_cart'),
    path('checkout/', views.checkout, name='checkout'),

]
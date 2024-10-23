from django.urls import path
from .import views

app_name ='userdash'

urlpatterns = [
        path('userdash/',views.userdash,name="userdash"),
        path('create_address/',views.create_address,name='create_address'),
        path('edit_address/<int:pk>',views.edit_address,name='edit_address'),
        path('default/<int:pk>',views.default,name='default'),
        path('change_password/',views.change_password,name='change_password'),
        path('edit_profile/',views.edit_profile,name='edit_profile'),
        path('delete_address/<int:pk>/',views.delete_address,name='delete_address'),  
        path('wishlist',views.wishlist,name='wishlist'), 
        path('add_to_wishlist',views.add_to_wishlist,name='add_to_wishlist'),
        path('wishlist_to_cart',views.wishlist_to_cart,name='wishlist_to_cart'),
        path('check_variant_in_wishlist/', views.check_variant_in_wishlist, name='check_variant_in_wishlist'),
        path('remove_wishlist/<int:pk>/',views.remove_wishlist,name='remove_wishlist')


]
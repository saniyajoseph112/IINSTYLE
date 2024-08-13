from django.urls import path, include
from .import views

app_name='product'


urlpatterns = [
     path('list_product/',views.list_product,name='list_product'),
     path('create/',views.create,name='create'),
     path('edit/<int:pk>/',views.edit,name='edit'),
     path('delete/<int:pk>/',views.delete,name='delete'),
     path('details/<int:pk>/',views.product_details,name='details'),
     path('product_image/<int:pk>/',views.product_image,name='product_image'),
     path('remove/<int:pk>/',views.remove,name='remove'),
     path('review/<int:pk>/',views.review,name='review'),
     path('list_varient/<int:pk>/',views.list_varient,name='list_varient'),
     path('create_varient/<int:pk>/',views.create_varient,name='create_varient'),
     path('edit_varient/<int:pk>/',views.edit_varient,name='edit_varient'),
     path('delete_varient/<int:pk>/',views.delete_varient,name='delete_varient'),
    
]
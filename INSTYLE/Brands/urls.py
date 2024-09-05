from django.urls import path
from .import views

app_name='Brands'

urlpatterns = [
      path('create',views.create,name='create'),
      path('list_brand',views.list_brand,name='list_brand'),
      path('edit<int:pk>',views.edit,name='edit'),
      path('delete<int:pk>',views.delete,name='delete'),


    
]
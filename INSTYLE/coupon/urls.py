from django.urls import path
from .import views

app_name='coupon'

urlpatterns = [
    path('coupon_list',views.coupon_list,name='coupon_list'),
    path('create_coupon',views.create_coupon,name='create_coupon'),
    path('edit_coupon/<int:pk>/',views.edit_coupon,name='edit_coupon'),
    path('coupon_status/<int:pk>/',views.coupon_status,name='coupon_status'),
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),
    path('remove_coupon/',views.removecoupon,name='remove_coupon'),
]
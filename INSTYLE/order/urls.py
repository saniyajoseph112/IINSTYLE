from django.urls import path, include
from .import views

app_name='order'


urlpatterns = [
     path('order_verification/',views.order_verification,name='order_verification'),
     path('order_success/',views.order_success,name='order_success'),
     path('order_list/',views.order_list,name='order_list'),
     path('admin_orders_details/<int:pk>/',views.admin_orders_details, name='admin_orders_details'),
     path('order_status/<int:pk>/',views.order_status, name='order_status'),
     path('online_payment/',views.Online_payment,name='online_payment'),
     path('online_payment_handler/',views.online_payment_post,name='online_payment_handler'),
     path('cancel_order/<int:pk>/',views.cancel_order,name='cancel_order'),
     path('return_order/<int:pk>/',views.return_order,name='return_order'),
     path('return_requests/',views.admin_return_requests,name='return_requests'),
     path('admin_return_approval/<int:pk>/',views.admin_return_approval,name='admin_return_approval'),
     path('user_invoice/<int:pk>/',views.user_invoice,name='user_invoice'),
     path('individual_return/<int:pk>/',views.individual_return,name='individual_return'),
]

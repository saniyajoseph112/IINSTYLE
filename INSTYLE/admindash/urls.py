from django.urls import path
from .import views

app_name='admindash'

urlpatterns = [
    path('login',views.admin_login,name='login'),
    path('admin_dash',views.admin_dash,name='admin_dash'),
    path('admin_user',views.admin_user,name='admin_user'),
    path('user_block/<int:user_id>/', views.user_block, name='user_block'),
    path('user_unblock/<int:user_id>/', views.user_unblock, name='user_unblock'),
]
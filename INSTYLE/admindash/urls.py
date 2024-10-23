from django.urls import path
from .import views

app_name='admindash'

urlpatterns = [
    path('login',views.admin_login,name='login'),
    path('admin_dash',views.admin_dash,name='admin_dash'),
    path('admin_user',views.admin_user,name='admin_user'),
    path('user_block/<int:user_id>/', views.user_block, name='user_block'),
    path('user_unblock/<int:user_id>/', views.user_unblock, name='user_unblock'),
    # path('admin_home',views.admin_home, name='admin_home'),
    path('sales_report/',views.sales_report, name='sales_report'),
    path('order_date_filter/',views.order_date_filter, name='order_date_filter'),
    path(' best_selling_products/',views.best_selling_products, name='best_selling_products'),
    path('best_selling_categories/',views.best_selling_categories, name='best_selling_categories'),
    path('best_selling_brands/',views.best_selling_brands, name='best_selling_brands'),
]
from django.urls import path
from .import views

app_name = 'accounts'

urlpatterns = [
    path('',views.home,name="home"),
    path('register/',views.register,name="register"),
    path('verify_otp/', views.verify_otp, name="verify_otp"),
    path('resend_otp/',views.resend_otp,name="resend_otp"),
    path('shop_page/',views.shop_page,name="shop_page"),
    path('login/',views.login,name="login"),
    path('logout/',views.logout,name="logout"),
    path('product_detailuser/<int:pk>/',views.product_detail_user,name="product_detailuser"),
    path('search/',views.search,name="search"),
    path('password-reset/',views.password_reset_request, name='password_reset'),
    path('password-reset-done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('about_us',views.about_us,name='about_us'),
    path('contact_us',views.contact_us,name='contact_us'),
]
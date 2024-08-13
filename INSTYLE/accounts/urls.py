from django.urls import path
from .import views

app_name = 'accounts'

urlpatterns = [
    path('',views.home,name="home"),
    path('register/',views.register,name="register"),
    path('verify_otp/', views.verify_otp, name="verify_otp"),
    path('resend_otp/',views.resend_otp,name="resend_otp"),
    path('shop_page/',views.shop_page,name="shop_page"),
    path('userdash/',views.userdash,name="userdash"),
    path('login/',views.login,name="login"),
    path('logout/',views.logout,name="logout"),
    path('product_detailuser/<int:pk>/',views.product_detail_user,name="product_detailuser"),

]
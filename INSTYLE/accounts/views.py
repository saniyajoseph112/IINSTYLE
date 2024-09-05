from django.shortcuts import render
from .forms import OtpForm, UserRegister
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth import logout as auth_logout
import logging
from django.utils import timezone
from product.models import *
from .forms import Emailauthentication
from category.models import *
from Brands.models import *
from django.http import JsonResponse



# Create your views here.
logger = logging.getLogger(__name__)
User = get_user_model()

def home(request):
    products =Products.objects.all()
    return render (request ,'User_side/home.html',{'products':products})

def login(request):
    if request.method == 'POST':
        form = Emailauthentication(request, data=request.POST)
        logger.debug(f"Form Valid: {form.is_valid()}")  # Debug statement
        if form.is_valid():
            user = form.get_user()
            logger.debug(f"Authenticated User: {user}")
            if user and user.is_active and not user.is_blocked:
                auth_login(request, user)
                return redirect('accounts:home')
        else:
            logger.debug(form.errors)  # Print out the form errors for debugging
    
    form = Emailauthentication()
    return render(request, 'user_side/login.html', {'form':form})


def logout(request):
    auth_logout(request)
    return redirect('accounts:home')



def shop_page(request):
    LH = request.GET.get('LH')
    HL = request.GET.get('HL')
    AR = request.GET.get('AR')
    NN = request.GET.get('NN')
    category_name = request.GET.get('category')
    brand_name = request.GET.get('brand')

    # Filter products based on sorting options
    if LH == "Low_to_High":
        products = Products.objects.order_by('offer_price')
    elif HL == "High_to_Low":
        products = Products.objects.order_by('-offer_price')
    elif AR == "average_rating":
        products = Products.objects.order_by('-average_rating')  
    elif NN == "Newness":
        products = Products.objects.order_by('-created_at')
    else:
        products = Products.objects.all()

    # Filter products by category if a category is selected
    if category_name:
        products = products.filter(product_category__category_name=category_name)

    # Filter products by brand if a brand is selected
    if brand_name:
        products = products.filter(product_brand__brand_name=brand_name)    
    
    categories = Category.objects.all()
    brands = Brand.objects.all()

    return render(request, 'user_side/shop.html', {'products': products, 'categories': categories, 'brands': brands})


def register(request):
    if request.method == 'POST':
        forms=UserRegister(request.POST)
        if forms.is_valid():
            User_data=forms.save(commit=False)
            User_data.is_active =False


            request.session['user_data']= {
                'first_name': User_data.first_name,
                'last_name': User_data.last_name,
                'email': User_data.email,
                'password': forms.cleaned_data.get('password')
            }

         #gerenate otp
            otp = get_random_string(length=6, allowed_chars='1234567890')
            print(otp)
            request.session['otp'] = otp   

            subject = 'Your OTP Code'
            message = f"""
            Dear {User_data.first_name},

            Welcome to INSTYLE!

            Thank you for joining our fashion community. We are thrilled to have you on board and can't wait for you to explore our latest collections and exclusive offers.

            To complete your registration, please verify your email address using the One-Time Password (OTP) provided below:

            Your OTP: {otp}

            Enter this OTP on the website to verify your account and get started.

            If you have any questions or need assistance, feel free to reach out to our support team at support@instyle.com.

            Stay stylish!

            Best regards,
            The INSTYLE Team
            """
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [User_data.email]
            
            send_mail(subject, message, email_from, recipient_list)

            return redirect('accounts:verify_otp')
    
    forms = UserRegister()
    return render(request, 'user_side/register.html', {'forms':forms})

        


def verify_otp(request):
    if request.method=='POST':
        forms=OtpForm(request.POST)
        if forms.is_valid():
            otp = forms.cleaned_data.get('otp')
            if otp == request.session.get('otp'):
                # OTP is correct, save the user data
                user_data = request.session.get('user_data')
                email = user_data.get('email')
                try:
                    # Check if a user with this email already exists
                    if User.objects.filter(email=email).exists():
                        user = User.objects.get(email=email)
                        messages.warning(request, 'User with this email already exists. Logging you in.')
                    else:
                        user = User.objects.create_user(
                            first_name=user_data.get('first_name'),
                            last_name=user_data.get('last_name'),
                            email=email,
                            password=user_data.get('password'),
                        )
                        user.is_active = True
                        user.save()

                        # Clear the session data
                        del request.session['user_data']
                        del request.session['otp']

                    return redirect('accounts:login')
                except IntegrityError:
                    messages.error(request, 'An error occurred while creating the user. Please try again.')
            else:
                forms.add_error('otp', 'Invalid OTP')
    else:
        forms= OtpForm()
    return render(request, 'user_side/verify.html', {'forms': forms})




def resend_otp(request):
    user_data = request.session.get('user_data')
    if user_data:
        otp = get_random_string(length=6, allowed_chars='1234567890')
        logger.debug(f"Generated OTP: {otp}")  # Debug statement

        otp_generation_time = timezone.now().isoformat()
        logger.debug(f"OTP Generation Time: {otp_generation_time}")  # Debug statement

        print(otp)

        request.session['otp'] = otp
        request.session['otp_generation_time'] = otp_generation_time

        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user_data['email']],
                fail_silently=False,
            )
            messages.success(request, 'A new OTP has been sent to your email.')
        except Exception as e:
            logger.error(f"Error sending email: {e}")  # Log email sending error
            messages.error(request, 'Failed to send OTP. Please try again later.')
    else:
        messages.error(request, 'User data not found. Please register again.')
    return redirect('accounts:verify_otp')




def product_detail_user(request,pk):
    products=Products.objects.get(id=pk) 
    images = ProductImage.objects.filter(product=products)
    related_products=Products.objects.filter(product_category=products.product_category)
    varients=ProductVariant.objects.filter(product=products)
    reviews=Review.objects.filter(product=products)
    return render(request,'user_side/product_detailuser.html',{'products':products,'images':images,'related_products':related_products,'reviews':reviews,'varients':varients}) 



def search(request):
    query = request.GET.get('q', '')
    print(query)
    if query:
        results = Products.objects.filter(
            product_name__icontains=query
        ) | Products.objects.filter(
            product_brand__brand_name__icontains=query
        ) | Products.objects.filter(
            product_description__icontains=query
        )
        
        data = {
            'results': [
                {
                    'name': result.product_name,
                    'url': f'/product/product-details/{result.id}/',  # Ensure this matches your URL pattern
                    'thumbnail': result.thumbnail.url if result.thumbnail else ''
                }
                for result in results
            ]
        }
    else:
        data = {'results': []}

    return JsonResponse(data)


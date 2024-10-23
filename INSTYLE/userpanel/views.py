from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import *
from userpanel.models import *
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
from order.models import*
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Products, ProductVariant
from django.http import JsonResponse
import json  # Importing the json module from Python standard library
from cart.models import *


# Create your views here.



def userdash(request):
    user = request.user.id  # Directly use request.user since it is already an authenticated User instance
    user_data = User.objects.get(id=user)
    user_address = UserAddress.objects.filter(user=user,is_deleted=False)
    orders= OrderMain.objects.filter(user=request.user.id).order_by('-updated_at')
    balance = 0  
    wallets = None 
    try:
        wallets = Wallet.objects.get(user=user)
        balance = wallets.balance
    except Wallet.DoesNotExist:
        pass  
    
    transactions = Transaction.objects.filter(wallet=wallets).order_by('-id')

    return render(request, 'user_side/userdash.html', {'user_data': user_data, 'user_address': user_address,'balance': balance,
                                                  'transactions':transactions,'wallets':wallets, 'orders':orders })


def create_address(request):
    if request.method == 'POST':
       user=User.objects.get(id = request.user.id)
       name =request.POST.get('name')
       house_name=request.POST.get('house_name')
       street_name=request.POST.get('street_name')
       pin_number =request.POST.get('pin_number')
       district=request.POST.get('district')
       state=request.POST.get('state')
       country=request.POST.get('country')
       phone_number=request.POST.get('phone_number')
       status=request.POST.get('status')=='on'
        


    user_address=UserAddress.objects.create(
            user= user,
            name=name,
            house_name=house_name,
            street_name= street_name,
            pin_number=  pin_number,
            district=district,
            state= state,
            country= country,
            phone_number=phone_number,
            status=status,
        )
    if status:
                UserAddress.objects.filter(user=request.user, status=True).update(status=False)

    user_address.save()
    return redirect('userdash:userdash')




def default(request,pk):
    address=UserAddress.objects.get(id=pk,user=request.user)
    default=UserAddress.objects.filter(user=request.user,status=True).update(status=False)
    address.status = True
    address.save()
    return redirect('userdash:userdash')


def edit_address(request,pk):
    user_data =UserAddress.objects.get(id=pk)
    
    if request.method == 'POST':
       name =request.POST.get('name')
       house_name=request.POST.get('house_name')
       street_name=request.POST.get('street_name')
       pin_number =request.POST.get('pin_number')
       district=request.POST.get('district')
       state=request.POST.get('state')
       country=request.POST.get('country')
       phone_number=request.POST.get('phone_number')
       status=request.POST.get('status')=='on'
       
       user_data.name = name
       user_data.house_name = house_name
       user_data.street_name = street_name
       user_data.pin_number = pin_number
       user_data.district = district
       user_data.state = state
       user_data.country = country
       user_data.phone_number = phone_number
       user_data.status = status
       user_data.save()

       messages.success(request, 'user address updated successfully.')
       return redirect('userdash:userdash')


    return render(request,'user_side/edit_address.html',{'user_data':user_data} )  


def delete_address(request, pk):
    user_data = UserAddress.objects.get(id=pk)
    user_data.is_deleted = not user_data.is_deleted
    user_data.save()
    return redirect('userdash:userdash')  # No pk argument is passed here

    




def change_password(request):
    if request.method == 'POST':
        user = request.user  # Use the authenticated user directly
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')


        if user.check_password(old_password):
            if new_password == confirm_password and new_password != old_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully')

                user = authenticate(username=request.user, password=new_password)
                if user is not None:
                    login(request, user)
                else:
                    messages.error(request, 'Authentication failed. Please login again.')
                
                return redirect('userdash:userdash')
            else:
                messages.error(request, 'New passwords do not match or are the same as the old password')
        else:
            messages.error(request, 'Old password is incorrect')

        return redirect('userdash:userdash')

    return redirect('userdash:userdash')


def edit_profile(request):
    if request.method=="POST":
        user = User.objects.get(id=request.user.id)
        user.first_name=request.POST.get('firstname')
        user.last_name=request.POST.get('lastname')
        user.save()

    return redirect('userdash:userdash')


def wishlist(request):
    wishlists = Wishlist.objects.filter(user=request.user)
    return render(request,'user_side/wish_list.html', {'wishlists': wishlists})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
import json
from .models import Wishlist, ProductVariant

@require_POST
@csrf_protect
@login_required
def add_to_wishlist(request):
    data = json.loads(request.body)
    variant_id = data.get('variant_id')

    try:
        if not variant_id:
            return JsonResponse({'success': False, 'error': 'Variant ID is missing'}, status=400)

        variant = ProductVariant.objects.get(id=variant_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, variant=variant)

        if created:
            return JsonResponse({'success': True, 'action': 'added'})
        else:
            wishlist_item.delete()  # Remove from wishlist
            return JsonResponse({'success': True, 'action': 'removed'})

    except ProductVariant.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Variant not found'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    


@require_POST
@csrf_protect
@login_required
def wishlist_to_cart(request):
    print("Add to cart view called")
    
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
   
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            product = variant.product
        except ProductVariant.DoesNotExist:
            messages.error(request, "The selected variant does not exist.")
            return JsonResponse({'error': 'Variant does not exist'}, status=400)

        if not request.user.is_authenticated:
            messages.error(request, "You need to be logged in to add items to the cart.")
            return JsonResponse({'error': 'User is not authenticated'}, status=403)
        
        user = request.user
        print(user)

        if not variant.variant_status:
            messages.error(request, "This variant is currently inactive.")
            return JsonResponse({'error': 'Variant is inactive'}, status=400)

        if not product.is_active:
            messages.error(request, "This product is currently inactive.")
            return JsonResponse({'error': 'Product is inactive'}, status=400)

        if variant.variant_stock < 1:
            messages.error(request, "This variant is out of stock.")
            return JsonResponse({'error': 'Variant is out of stock'}, status=400)

        cart, created = Cart.objects.get_or_create(user=user)

        cartitem, created = CartItem.objects.get_or_create(
            product=product,
            variant=variant,
            cart=cart,
            defaults={'quantity': 1},
        )

        if not created:
            cartitem.quantity += 1
            cartitem.save()

        messages.success(request, "Item added to cart successfully.")
        return JsonResponse({'message': 'Item added to cart successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)





@login_required
def check_variant_in_wishlist(request):
    variant_id = request.GET.get('variant_id')
    in_wishlist = Wishlist.objects.filter(user=request.user, variant__id=variant_id).exists()
    return JsonResponse({'in_wishlist': in_wishlist})

def remove_wishlist(request,pk):

    try:
        item = get_object_or_404(Wishlist, id=pk)
        item.delete()
        return redirect('userdash:wishlist')
    except:
        return redirect('userdash:wishlist')






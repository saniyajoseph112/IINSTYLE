import json
from django.shortcuts import render
from product.models import *
from django.shortcuts import get_object_or_404, redirect
from .models import ProductVariant, Cart, CartItem
from django.contrib import messages 
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from userpanel.models import *
from coupon.models import *
from django.contrib.auth.decorators import login_required


def cart(request):
    try:
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).order_by('-cart__updated_at')
        cart_prices = CartItem.objects.filter(cart=cart, is_active=True)
        sub_total = sum(item.sub_total() for item in cart_prices)

        return render(request, 'cart_side/cart.html', {'cart_items': cart_items,'sub_total':sub_total})
    
    except:
        return render(request, 'cart_side/cart.html')




def add_to_cart(request):
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

       

        messages.success(request, "Item added to cart successfully.")
        return JsonResponse({'message': 'Item added to cart successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def update_cart_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity'))

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.quantity = new_quantity
            cart_item.save()

            # Recalculate totals
            cart_items = CartItem.objects.filter(cart__user=request.user, is_active=True)
            new_total = sum(item.sub_total() for item in cart_items)
            sub_total = sum(item.sub_total() for item in cart_items)
            item_total = sub_total

            response = {
                'success': True,
                'new_total': round(new_total, 2),
                'sub_total': round(sub_total, 2),
                'item_total':round(item_total, 2),
                'item_sub_total': round(cart_item.sub_total(), 2)  # Subtotal for the specific item
            }

        except CartItem.DoesNotExist:
            response = {
                'success': False,
                'message': 'Item not found in cart.'
            }

        return JsonResponse(response)

    return JsonResponse({'success': False})

def checkout(request):
    user = User.objects.get(id=request.user.id)
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    user_address = UserAddress.objects.filter(user=user,is_deleted=False)

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        pass

        
    cart_items = CartItem.objects.filter(cart=cart,is_active=True)
    sub_total = sum(item.sub_total() for item in cart_items)

    wallet_balance = sub_total

    for item in cart_items:
        if item.variant.variant_stock < 1:
            messages.error(request, 'Out of stock')
            return redirect('cart:cart')
    
        if not item.product.is_active: 
            messages.error(request, 'Product is out of stock')
            return redirect('cart:cart')
        
        if not item.variant.variant_status:
            messages.error(request, 'Variant is out of stock')
            return redirect('cart:cart')

    # If all checks are passed, render the checkout page
    
    available_coupons = Coupon.objects.filter(status=True, expiry_date__gte=timezone.now()) 
    used_coupons = UserCoupon.objects.filter(user=request.user).values_list('coupon',flat=True) 
    available_coupons = available_coupons.exclude(id__in=used_coupons)

    
            

    user_address = UserAddress.objects.filter(user=request.user.id,is_deleted=False).order_by('-status', 'id')
    print(sub_total)

    return render(request,'cart_side/checkout.html', {
            'cart_items': cart_items,
            'sub_total': sub_total,
            'user_address': user_address,
            'discount':0,
            'discount_amount':0,
            'coupon_name':"Not Applyed",
            'available_coupons': available_coupons,
            'wallet_balance' : wallet_balance,
            })


    


def update_selected_address(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            address_id = data.get('address_id')
            if address_id:
                print("address_id",address_id)
            else:
                print("NOne Foundedddd")

            if not address_id:
                return JsonResponse({'status': 'error', 'message': 'Address ID is required'}, status=400)

            # Get the address object
            address = UserAddress.objects.filter(id=address_id, user=request.user).first()

            if not address:
                return JsonResponse({'status': 'error', 'message': 'Address not found'}, status=404)

            # Update all addresses to set status to False
            UserAddress.objects.filter(user=request.user).update(status=False)

            # Set the selected address status to True
            address.status = True
            address.save()

            return JsonResponse({'status': 'success', 'message': 'Address updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
        

def remove_item_cart(request,pk):
    cart_items = CartItem.objects.get(id=pk)
    cart_items.delete()

    return redirect('cart:cart')



def create_address2(request):
    user_addresses = UserAddress.objects.filter(user=request.user).order_by('-status', 'id')
    context = {
        'user_addresses': user_addresses,
    }
    if request.method == 'POST':
        # Fetch the user object using the request's user ID
        user = User.objects.get(id=request.user.id)

        # Safely retrieve and strip form data
        name = request.POST.get('name', '').strip()
        house_name = request.POST.get('house_name', '').strip()
        street_name = request.POST.get('street_name', '').strip()
        pin_number = request.POST.get('pin_number', '').strip()
        district = request.POST.get('district', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        status = request.POST.get('status') == 'on'

        # Validation checks
        if not name:
            messages.error(request, 'Name Required')
            return redirect('cart:checkout')

        if not house_name:
            messages.error(request, 'House name Required')
            return redirect('cart:checkout')

        if not street_name:
            messages.error(request, 'Street name Required')
            return redirect('cart:checkout')

        if not pin_number:
            messages.error(request, 'PIN number Required')
            return redirect('cart:checkout')

        if not district:
            messages.error(request, 'District Required')
            return redirect('cart:checkout')

        if not state:
            messages.error(request, 'State Required')
            return redirect('cart:checkout')

        if not country:
            messages.error(request, 'Country Required')
            return redirect('cart:checkout')

        if not phone_number:
            messages.error(request, 'Phone number Required')
            return redirect('cart:checkout')

        if not pin_number.isdigit() or len(pin_number) != 6:
            messages.error(request, "Please enter a valid 6-digit PIN number.")
            return redirect('cart:checkout')

        if not phone_number.isdigit() or len(phone_number) not in [10, 12]:
            messages.error(request, "Please enter a valid phone number with 10 or 12 digits.")
            return redirect('cart:checkout')

        # Create and save the new address
        user_address= UserAddress.objects.create(
            user=user,
            name=name,
            house_name=house_name,
            street_name=street_name,
            pin_number=pin_number,
            district=district,
            state=state,
            country=country,
            phone_number=phone_number,
            status=status,

        )


        messages.success(request, 'Address added successfully.')
        return redirect('cart:checkout')

    # Render the template with context for GET requests
    return render(request, 'cart_side/address.html', context)



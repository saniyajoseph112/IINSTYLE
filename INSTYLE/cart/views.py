from django.shortcuts import render
from product.models import *
from django.shortcuts import get_object_or_404, redirect
from .models import ProductVariant, Cart, CartItem
from django.contrib import messages 
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

def cart(request):
    user = User.objects.get(id=request.user.id)
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        pass
        
    cart_items = CartItem.objects.filter(cart=cart,is_active=True)
    sub_total = sum(item.sub_total() for item in cart_items)

    return render(request, 'cart_side/cart.html', {'cart_items': cart_items,'sub_total':sub_total})


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

        if not created:
            cartitem.quantity += 1
            cartitem.save()

        messages.success(request, "Item added to cart successfully.")
        return JsonResponse({'message': 'Item added to cart successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def update_cart_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity'))

        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.quantity = new_quantity
        cart_item.save()

        cart_items = CartItem.objects.filter(cart__user=request.user, is_active=True)
        new_total = sum(item.sub_total() for item in cart_items)
        sub_total = sum(item.sub_total() for item in cart_items)

        response = {
            'success': True,
            'new_total': round(new_total, 2),
            'sub_total': round(sub_total, 2),
            'item_sub_total': round(cart_item.sub_total(), 2)  # Assuming you want to return the subtotal for the specific item
        }

        return JsonResponse(response)

    return JsonResponse({'success': False})



def checkout(request):
    user = User.objects.get(id=request.user.id)
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)

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
    return render(request, 'cart_side/checkout.html', {'cart_items': cart_items})
    
        

def remove_item_cart(request,pk):
    cart_items = CartItem.objects.get(id=pk)
    cart_items.delete()

    return redirect('cart:cart')

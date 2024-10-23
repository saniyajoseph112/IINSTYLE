from django.shortcuts import render,redirect,get_object_or_404
from coupon.models import Coupon
from django.contrib import messages 
from cart.models import *
from django.http import JsonResponse


# Create your views here.
def coupon_list(request):
     coupons = Coupon.objects.all()

     return render(request, 'Coupon_side/coupon.html',{'coupons':coupons})

def create_coupon(request):
    if request.method == 'POST':
        coupon_name = request.POST.get('coupon_name').strip()
        minimum_amount = request.POST.get('minimum_amount')
        maximum_amount = request.POST.get('maximum_amount')
        discount = request.POST.get('discount')
        expiry_date = request.POST.get('expiry_date')
        coupon_code = request.POST.get('generated_coupon_code')
        status = request.POST.get('status') == 'on'
        errors = []
        try:
            minimum_amount = int(minimum_amount) if minimum_amount else None
            maximum_amount = int(maximum_amount) if maximum_amount else None
            discount = int(discount) if discount else None
        except ValueError:
            messages.error(request, 'Minimum Amount, Maximum Amount, and Discount must be valid numbers.')
            return redirect('coupon:create_coupon')
        if minimum_amount > 9000:
            errors.append('Minimum Amount Only Add Up To ₹9000')
        elif minimum_amount < 1000:
            errors.append('Minimum Amount Should Be Greater Than ₹1000')
        if maximum_amount > 10000:
            errors.append('Maximum Amount Only Add Up To ₹10000')
        elif maximum_amount < 4000:
            errors.append('Maximum Amount Should be Greater than ₹4000')
        if not coupon_name:
            errors.append('Coupon Name Required')
        if minimum_amount is None or maximum_amount is None:
            errors.append('Both Minimum and Maximum Amounts are Required')
        elif minimum_amount > maximum_amount:
            errors.append('Minimum Amount Should be Lesser than Maximum Amount')
        if discount is None:
            errors.append('Discount is Required')
        elif discount > 70:
            errors.append('Discount Can Only Be Up to 70%')
        if not expiry_date:
            errors.append('Expiry Date is Required')
        if not coupon_code:
            errors.append('Coupon Code is Required')
        elif Coupon.objects.filter(coupon_code__iexact=coupon_code).exists():
            errors.append('A Coupon with this Code Already Exists')
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('coupon:create_coupon')
        Coupon.objects.create(
            coupon_name=coupon_name,
            minimum_amount=minimum_amount,
            maximum_amount=maximum_amount,
            discount=discount,
            expiry_date=expiry_date,
            coupon_code=coupon_code,
            status=status
        )
        messages.success(request, 'Coupon Created Successfully')
        return redirect('coupon:create_coupon')
    else:
        return render(request, 'Coupon_side/create_coupon.html')
    

def edit_coupon(request, pk):
    coupon = get_object_or_404(Coupon, id=pk)
    if request.method == 'POST':
        errors = []
        coupon_name = request.POST.get('coupon_name', '').strip()
        minimum_amount = request.POST.get('minimum_amount', '').strip()
        maximum_amount = request.POST.get('maximum_amount', '').strip()
        discount = request.POST.get('discount', '').strip()
        expiry_date = request.POST.get('expiry_date', '').strip()
        coupon_code = request.POST.get('generated_coupon_code', '').strip()
        status = request.POST.get('status') == 'on'
        try:
            minimum_amount = int(minimum_amount) if minimum_amount else None
            maximum_amount = int(maximum_amount) if maximum_amount else None
            discount = int(discount) if discount else None
        except ValueError:
            errors.append('Minimum Amount, Maximum Amount, and Discount must be valid numbers.')
        if minimum_amount is not None:
            if minimum_amount > 9000:
                errors.append('Minimum Amount Only Up To ₹9000')
            elif minimum_amount < 1000:
                errors.append('Minimum Amount Should Be Greater Than ₹1000')
        else:
            errors.append('Minimum Amount is Required')
        if maximum_amount is not None:
            if maximum_amount > 10000:
                errors.append('Maximum Amount Only Up To ₹10000')
            elif maximum_amount < 4000:
                errors.append('Maximum Amount Should Be Greater Than ₹4000')
        else:
            errors.append('Maximum Amount is Required')
        if minimum_amount is not None and maximum_amount is not None:
            if minimum_amount > maximum_amount:
                errors.append('Minimum Amount Should Be Lesser than Maximum Amount')
        if discount is not None:
            if discount > 70:
                errors.append('Discount Can Only Be Up to 70%')
        else:
            errors.append('Discount is Required')
        if not expiry_date:
            errors.append('Expiry Date is Required')
        if not coupon_code:
            errors.append('Coupon Code is Required')
        elif Coupon.objects.filter(coupon_code__iexact=coupon_code).exclude(id=pk).exists():
            errors.append('A Coupon with this Code Already Exists')
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'Coupon_side/edit_coupon.html', {'coupon': coupon})
        # Update coupon object and save
        coupon.coupon_name = coupon_name
        coupon.minimum_amount = minimum_amount
        coupon.maximum_amount = maximum_amount
        coupon.discount = discount
        coupon.expiry_date = expiry_date
        coupon.coupon_code = coupon_code
        coupon.status = status
        coupon.save()
        messages.success(request, 'Coupon Updated Successfully')
        return redirect('coupon:coupon_list')
    else:
        return render(request, 'Coupon_side/edit_coupon.html', {'coupon': coupon})

def coupon_status(request, pk):
    if request.method =='POST':
        try:
            coupon = get_object_or_404(Coupon, id=pk)
            coupon.status = not coupon.status
            coupon.save()
            messages.success(request, 'Coupon status updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating coupon status: {e}')
    return redirect('coupon:coupon_list')


def apply_coupon(request):
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = sum(item.sub_total() for item in cart_items)
        
        if coupon:
            try:
                coupon_code = Coupon.objects.get(coupon_code=coupon)

                if total > coupon_code.minimum_amount:
                    discount = coupon_code.discount
                    discount_amount = (total * discount / 100)
                    discount_amount = min(discount_amount, coupon_code.maximum_amount)
                    new_total = total - discount_amount
                    wallet_balance = round(new_total, 2)

                    # Save coupon code in session
                    request.session['applied_coupon'] = coupon_code.coupon_code
                    request.session.modified = True  # Ensures session is saved
                    
                    # Debugging to ensure session value is set
                    print("Coupon applied:", request.session.get('applied_coupon'))

                    return JsonResponse({
                        'success': True,
                        'new_total': round(new_total, 2),
                        'discount_amount': round(discount_amount, 2),
                        'discount': discount,
                        'wallet_balance':wallet_balance,
                        'message': 'Coupon applied successfully!'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': f'Coupon only available for orders over {coupon_code.minimum_amount}'
                    })
            except Coupon.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid coupon code'
                })

        return JsonResponse({
            'success': False,
            'message': 'No coupon code provided'
        })
    

def removecoupon(request):
    if request.method == 'POST':
        response = {'success': False}

        # Get the user's cart and active cart items
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Remove the applied coupon from the session
        request.session.pop('applied_coupon', None)

        # Calculate the new total after removing the coupon
        new_total = sum(item.sub_total() for item in cart_items)
        wallet_balance = new_total

        # Update the response with success and new total
        response.update({
            'success': True,
            'message': 'Coupon removed successfully.',
            'new_total': round(new_total, 2),
            'wallet_balance':round(wallet_balance, 2),
            'discount': 0
        })

        return JsonResponse(response)


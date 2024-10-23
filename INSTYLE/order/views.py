from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User
from cart.models import Cart, CartItem
from django.contrib import messages
from order.models import OrderMain, OrderSub, OrderAddress
from userpanel.models import UserAddress
from django.http import HttpResponse
import razorpay
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime
import json
from django.utils.crypto import get_random_string
from coupon.models import *
from decimal import Decimal
from  order.models import*




def order_verification(request):
    if request.method == "POST":
        user = User.objects.get(id=request.user.id)
        
        # Ensure wallet exists or create one if it doesn't
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet_balance = wallet.balance
        
        # Retrieve cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            messages.error(request, 'Cart does not exist')
            return redirect('cart:checkout')

        cart_items = CartItem.objects.filter(cart=cart)
        payment_option = request.POST.get('payment_option')
        sub_total = sum(item.sub_total() for item in cart_items)

        # Retrieve address
        try:
            address = UserAddress.objects.get(user=user, status=True)
        except UserAddress.DoesNotExist:
            messages.error(request, 'No address found')
            return redirect('cart:checkout')

        # Check stock and status of cart items
        for item in cart_items:
            if item.variant.variant_stock < 1:
                messages.error(request, 'Out of stock')
                return redirect('cart:checkout')

            if not item.product.is_active:
                messages.error(request, 'Product is out of stock')
                return redirect('cart:checkout')

            if not item.variant.variant_status:
                messages.error(request, 'Variant is out of stock')
                return redirect('cart:checkout')

        # Coupon logic
        coupon_code = request.session.get('applied_coupon')
        discount = 0
        discount_amount = 0
        final_amount = sub_total  # Default final amount is sub_total

        if coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                if sub_total >= coupon.minimum_amount:
                    discount = coupon.discount
                    discount_amount = (sub_total * discount / 100)
                    discount_amount = min(discount_amount, coupon.maximum_amount)
                    final_amount = sub_total - discount_amount
                else:
                    messages.error(request, f'Coupon only available for orders over {coupon.minimum_amount}')
            except Coupon.DoesNotExist:
                pass

        # Add wallet balance to the context
        context = {
            'cart_total': sub_total,
            'wallet_balance': wallet_balance,  # Add wallet balance to the context
            'cart_items': cart_items,
        }

        # Handle payment options
        if payment_option == "Online Payment":
            return redirect('order:online_payment')

        elif payment_option == "Cash On Delivery":
            if final_amount > 3500:
                messages.error(request, "Cash On Delivery Only Available Upto 5000")
                return redirect('cart:checkout')
            else:
                # Create order and related objects
                order_address = OrderAddress.objects.create(
                    name=address.name,
                    house_name=address.house_name,
                    street_name=address.street_name,
                    pin_number=address.pin_number,
                    district=address.district,
                    state=address.state,
                    country=address.country,
                    phone_number=address.phone_number,
                )

                order_main = OrderMain.objects.create(
                    user=user,
                    address=order_address,
                    total_amount=sub_total,
                    discount_amount=discount_amount,
                    final_amount=final_amount,
                    order_status="confirmed",
                    payment_option=payment_option,
                    order_id="ORDER" + str(user.id) + str(cart.id),
                )

                for item in cart_items:
                    OrderSub.objects.create(
                        user=user,
                        main_order=order_main,
                        variant=item.variant,
                        price=item.variant.product.offer_price,
                        quantity=item.quantity,
                        is_active=True,
                    )

                if coupon_code:
                    request.session.pop('applied_coupon', None)

                cart_items.delete()

                messages.success(request, 'Cash on Delivery Order Placed.')
                return redirect('order:order_success')

        elif payment_option == "Wallet":
            if wallet_balance >= final_amount:
                # Deduct the amount from the user's wallet
                wallet.balance -= final_amount
                wallet.save()

                # Create order and related objects
                order_address = OrderAddress.objects.create(
                    name=address.name,
                    house_name=address.house_name,
                    street_name=address.street_name,
                    pin_number=address.pin_number,
                    district=address.district,
                    state=address.state,
                    country=address.country,
                    phone_number=address.phone_number,
                )

                order_main = OrderMain.objects.create(
                    user=user,
                    address=order_address,
                    total_amount=sub_total,
                    discount_amount=discount_amount,
                    final_amount=final_amount,
                    order_status="confirmed",
                    payment_option=payment_option,
                    order_id="ORDER" + str(user.id) + str(cart.id),
                )

                for item in cart_items:
                    OrderSub.objects.create(
                        user=user,
                        main_order=order_main,
                        variant=item.variant,
                        price=item.variant.product.offer_price,
                        quantity=item.quantity,
                        is_active=True,
                    )
                if coupon_code:
                    request.session.pop('applied_coupon', None)
                cart_items.delete()

                messages.success(request, 'Order has been successfully placed using wallet.')
                return redirect('order:order_success')
            else:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('cart:checkout')

        else:
            # Handle unexpected payment options
            messages.error(request, 'Invalid payment option selected.')
            return redirect('cart:checkout')

    # In case the request is not POST
    return redirect('cart:checkout')


def Online_payment(request):
    """Handles the GET request for the online payment."""
    try:
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user, is_active=True) 
        new_total = sum(item.sub_total() for item in cart_items) 

        # Handle coupon logic if applicable
        coupon_code = request.session.get('applied_coupon')
        discount = 0
        discount_amount = 0
        if coupon_code:
            try:
                
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                if new_total >= coupon.minimum_amount:
                    discount = coupon.discount
                    discount_amount = (new_total * discount / 100)
                    discount_amount = min(discount_amount, coupon.maximum_amount)
                    new_total = new_total - discount_amount
                else:
                    messages.error(request, f'Coupon only available for orders over {coupon.minimum_amount}')
            except Coupon.DoesNotExist:
                pass

        # Convert the total amount to paise
        new_total_paise = int(new_total * 100)

        # Create a Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
        payment = client.order.create({'amount': new_total_paise, 'currency': 'INR', 'payment_capture': 1})

        print(f"Razorpay order created: {payment}")  # Logging the payment object

        # Render the payment page with Razorpay details
        context = {
            'cart': new_total,
            'payment': payment,
            'razorpay_key_id': settings.RAZORPAY_KEY,
            'payment_amount': new_total_paise,
        
        }
        return render(request, 'order_side/online_payment.html', context)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('cart:checkout')
    

    

def online_payment_post(request):
    """Handles the POST request for processing the payment."""
    try:
        data = json.loads(request.body)
        print(f"Received payment data: {data}")  # Logging received data

        # Verify the payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
        params_dict = {
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }
        client.utility.verify_payment_signature(params_dict)

        current_user = request.user
        cart = Cart.objects.get(user=current_user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        address = UserAddress.objects.get(user=current_user, status=True, is_deleted=False)
        payment_option = "Online Payment"
        order_status = "Shipped"

        # Generate a unique order ID
        current_date_time = datetime.now()
        formatted_date_time = current_date_time.strftime("%H%m%S%Y")
        unique = get_random_string(length=4, allowed_chars='1234567890')
        user = str(request.user.id)
        order_id = user + formatted_date_time + unique

        payment_id = data.get('razorpay_payment_id')

        new_total = sum(item.sub_total() for item in cart_items)
        final_amount = new_total
        # Handle coupon logic if applicable
        coupon_code = request.session.get('applied_coupon')
        discount = 0
        discount_amount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                if new_total >= coupon.minimum_amount:
                    discount = coupon.discount
                    discount_amount = (new_total * discount / 100)
                    discount_amount = min(discount_amount, coupon.maximum_amount)
                    final_amount = new_total - discount_amount
                else:
                    messages.error(request, f'Coupon only available for orders over {coupon.minimum_amount}')
            except Coupon.DoesNotExist:
                pass

        # Create order address
        order_address = OrderAddress.objects.create(
            name=address.name,
            house_name=address.house_name,
            street_name=address.street_name,
            pin_number=address.pin_number,
            district=address.district,
            state=address.state,
            country=address.country,
            phone_number=address.phone_number
        )

        # Create the main order
        order_main = OrderMain.objects.create(
            user=current_user,
            address=order_address,
            total_amount=new_total,
            discount_amount=discount_amount,  # No coupon logic, so discount is 0
            final_amount=final_amount,
            payment_option=payment_option,
            order_id=order_id,
            order_status=order_status,
            payment_id=payment_id,
            payment_status=True
        )

        # Add order items
        for cart_item in cart_items:
            OrderSub.objects.create(
                user=current_user,
                main_order=order_main,
                variant=cart_item.variant,
                price=cart_item.product.offer_price,
                quantity=cart_item.quantity,
            )

            # Update the stock
            variant = cart_item.variant
            variant.variant_stock -= cart_item.quantity
            variant.save()

        # Clear cart after order
        if coupon_code:
            request.session.pop('applied_coupon', None)
        cart_items.delete()

        # Store order information in session
        request.session['order_id'] = order_main.order_id
        request.session['order_date'] = order_main.date.strftime("%Y-%m-%d")
        request.session['order_status'] = order_main.order_status

        print(f"Order created successfully: {order_main}")  # Logging order creation
        return JsonResponse({'success': True, 'message': 'Payment successful'})

    except json.JSONDecodeError:
        print("Invalid JSON received")
        return JsonResponse({'success': False, 'message': 'Invalid JSON'})

    except razorpay.errors.SignatureVerificationError as e:
        print(f"Razorpay signature verification failed: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Payment verification failed'})

    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)})


def order_success(request):


    return render(request, 'order_side/order.html')




def order_list(request):
    orders = OrderMain.objects.all().order_by('-updated_at') 
    return render(request,'order_side/order_list.html', {'orders':orders})

def admin_orders_details(request,pk):
     orders = OrderMain.objects.get(id=pk)
     order_sub = OrderSub.objects.filter(main_order=orders)

     return render(request, 'order_side/admin_order_details.html', {'orders': orders, 'order_sub': order_sub})

def order_status(request,pk):
    if request.method == 'POST':
        fk = pk
        order = get_object_or_404(OrderMain, id=pk)
        new_status = request.POST.get('order_status')
        
    if new_status:
        order.order_status = new_status
        order.save()
            
        return redirect('order:admin_orders_details',fk)
    else:
        return HttpResponse("No status selected", status=400)
    




def cancel_order(request, pk):
    try:
        order = OrderMain.objects.get(id=pk)
        order_items = OrderSub.objects.filter(main_order=order, is_active=True)
        reason = request.POST.get('reason','')
        print(reason)
        if not order.is_active:
            messages.error(request, 'Order item is already Canceled.')
            return redirect('userdash:userdash')
        
        for order_item in order_items:
            order_variant = order_item.variant
            order_quantity = order_item.quantity
            
            order_variant.variant_stock += order_quantity

        order.order_status = "Canceled"
        order.is_active = False
        order.reason =reason
        order.save()

        if order.payment_option in ["Online Payment", "Wallet"]:
            item_refund = Decimal('0')

            for item in order_items:
                item_amount = Decimal(str(item.price * item.quantity))
                order_amount = Decimal(str(order.total_amount))
                order_discount_amount = Decimal(str(order.discount_amount))

                item_discount_amount = (order_discount_amount * item_amount) / order_amount
                item_refund_amount = item_amount - item_discount_amount

                item_refund += item_refund_amount
                item.is_active = False
                item.main_order.final_amount -= item_refund
                item.save()

            if item_refund > 0:
                description = f"Refund for Cancel order {order.order_id}"
                transaction_type = "Credited"

                wallet, created = Wallet.objects.get_or_create(user=request.user)

                transaction = Transaction.objects.create(
                    wallet=wallet,
                    description=description,
                    amount=item_refund,
                    transaction_type=transaction_type,
                )

                wallet.balance += item_refund  # Ensure Decimal type for accurate calculation
                wallet.save()

            order.save()

        
        messages.success(request, 'Order has been successfully canceled.')
        
    except OrderMain.DoesNotExist:
        messages.error(request, 'Order does not exist.')

    return redirect('userdash:userdash')

def return_order(request, pk):
    if request.method == 'POST':
        try:
            order = get_object_or_404(OrderMain, id=pk)
            order_items = OrderSub.objects.filter(main_order=order)

            if not order.is_active:
                messages.error(request, 'Order item is already returned.')
                return redirect('userdash:userdash')

            if order.order_status in ['Pending', 'Confirmed', 'Shipped']:
                messages.error(request, 'Order cannot be returned at this stage.')
                return redirect('userdash:userdash')

            reason = request.POST.get('reason', '').strip()
            if not reason:
                messages.error(request, 'A reason must be provided for returns.')
                return redirect('userdash:userdash')

            ReturnRequest.objects.create(
                order_main=order,
                reason=reason
            )

            order.order_status = "Pending"
            order.save()

            messages.success(request, "Please wait for the admin's approval.")
            return redirect('userdash:userdash')

        except OrderMain.DoesNotExist:
            messages.error(request, "Order does not exist.")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('userdash:userdash')
    else:
        return redirect('userdash:userdash')




def admin_return_requests(request):
    search_query = request.GET.get('search', '').strip()

    if search_query:
        return_requests = ReturnRequest.objects.filter(order_main__order_id__icontains=search_query).order_by('-created_at')
    else:
        return_requests = ReturnRequest.objects.all().order_by('-created_at')

    # Pagination
    # paginator = Paginator(return_requests, 5)  # Show 10 return requests per page
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    return render(request, 'order_side/return_order.html', {
        'return_requests': return_requests,
        'search_query': search_query,
    })



def admin_return_approval(request, pk):
    if request.method == 'POST':
        return_request = get_object_or_404(ReturnRequest, id=pk)
        action = request.POST.get('action')
        
        if action == 'Approve':
            return_request.status = "Approved"
            return_request.save()
            
            refund_amount = Decimal('0.00')
            
            if return_request.order_sub:  # If specific item return

                item = return_request.order_sub
                main_order = item.main_order
                item_total_cost = Decimal(str(item.final_total_cost()))
                order_total_amount = Decimal(str(main_order.total_amount))
                order_discount_amount = Decimal(str(main_order.discount_amount))
                
                item_discount_amount = (order_discount_amount * item_total_cost) / order_total_amount
                refund_amount = item_total_cost - item_discount_amount
                
                item.is_active = False
                item.status = "Returned"
                item.save()
                
                order = return_request.order_main
                
                order.save()
                
                all_canceled = not main_order.ordersub_set.filter(is_active=True).exists()
                
                if all_canceled:  # If all items are canceled

                    main_order.order_status = 'Returned'
                    main_order.save()
                    
            else:  # If entire order return

                order = return_request.order_main
                active_items = order.ordersub_set.filter(is_active=True)
                
                for item in active_items:
                    item_total_cost = Decimal(str(item.final_total_cost()))
                    order_total_amount = Decimal(str(order.total_amount))
                    order_discount_amount = Decimal(str(order.discount_amount))

                    item_discount_amount = (order_discount_amount * item_total_cost) / order_total_amount
                    item_refund_amount = item_total_cost - item_discount_amount

                    refund_amount += item_refund_amount
                    item.is_active = False
                    item.status = "Returned"
                    item.save()

                order.order_status = 'Returned'
                order.is_active = False
            
                order.save()

            if refund_amount > 0 and return_request.order_main.payment_status:
                wallet, created = Wallet.objects.get_or_create(user=return_request.order_main.user)

                wallet.balance += refund_amount 
                wallet.updated_at = timezone.now()
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    amount=refund_amount,
                    description=f"Refund for {'order' if return_request.order_sub is None else 'item'} {return_request.order_main.order_id if return_request.order_sub is None else return_request.order_sub.variant.product.product_name}",
                    transaction_type='Credited'
                )
                
                messages.success(request, 'Return request approved and amount credited to the user\'s wallet.')
                return redirect('order:return_requests')
            else:
                messages.success(request, 'Return request approved. No payment was made or payment status is not confirmed.')
                return redirect('order:return_requests')
            
        elif action == "Reject":
            return_request.status = "Rejected"
            if return_request.order_sub:
                return_request.order_sub.status = "Return Rejected"
                return_request.order_sub.save()
            return_request.save()
            messages.success(request, 'Return request rejected.')
            return redirect('order:return_requests')
        
        else:
            messages.error(request, 'Invalid action.')
            return redirect('order:return_requests')

    return redirect('order:return_requests')


def user_invoice(request, pk):
    order_main = get_object_or_404(OrderMain, id=pk)
    order_sub = OrderSub.objects.filter(main_order=order_main, is_active=True)
    
    return render(request, 'order_side/user_invoice.html', {
        'order_main': order_main,
        'order_sub': order_sub
    })




def individual_return(request, pk):
    if request.method == "POST":
    
        # Fetch the order item, ensuring the user has access
        order_sub = get_object_or_404(OrderSub, id=pk, user=request.user)

        # Check if the order item has already been returned
        if not order_sub.is_active:
            messages.error(request, 'Order item is already Returned.')
            return redirect('userdash:userdash')

        # Check if the order status allows for a return
        if order_sub.main_order.order_status in ['Pending', 'Confirmed', 'Shipped', 'Canceled']:
            messages.error(request, 'Order cannot be returned at this stage.')
            return redirect('userdash:userdash')

        # Get the reason for the return from the POST data
        reason = request.POST.get('reason', '').strip()

        if not reason:
            messages.error(request, 'A reason must be provided for returns.')
            return redirect('userdash:userdash')

        # Create a return request
        ReturnRequest.objects.create(
            order_main=order_sub.main_order,
            order_sub=order_sub,
            reason=reason
        )

        # Update the order status to "Return Requested"
        order_sub.status = "Return Requested"
        order_sub.save()

        # Notify the user of successful return request submission
        messages.success(request, "Please wait for the admin's approval.")
        return redirect('userdash:userdash')
    return redirect('userdash:userdash')



    




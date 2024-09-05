from django.shortcuts import render,redirect
from accounts.models import *
from userpanel.models import *
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.



def userdash(request):
    user = request.user.id  # Directly use request.user since it is already an authenticated User instance
    user_data = User.objects.get(id=user)
    user_address = UserAddress.objects.filter(user=user,is_deleted=False)
    return render(request, 'user_side/userdash.html', {'user_data': user_data, 'user_address': user_address})


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





        








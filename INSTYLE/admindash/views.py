from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from accounts.models import User 
from utils.decorators import admin_required 

# Create your views here.

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_admin:
                login(request, user)
                return redirect('admindash:admin_dash')
            else:
                messages.error(request, 'You are not authorized to access this page.')
        else:
            messages.error(request, 'Invalid email or password.')
            
    return render(request, 'admin_side/admin_login.html')

@admin_required
def admin_dash(request):
    return render(request, 'admin_side/admin_dash.html')


@admin_required
def admin_user(request):
    users = User.objects.all()
    return render(request, 'admin_side/admin_user.html', {'users': users})


@admin_required
def user_block(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = True
    user.save()
    messages.success(request, 'User blocked successfully.')
    return redirect('admindash:admin_user')


@admin_required
def user_unblock(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = False
    user.save()
    messages.success(request, 'User unblocked successfully.')
    return redirect('admindash:admin_user')
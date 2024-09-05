from accounts.models import *
from social_core.pipeline.partial import partial
from django.contrib import messages

@partial
def save_user_details(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = {
        'first_name': details.get('first_name'),
        'last_name': details.get('last_name'),
        'email': details.get('email'),
    }
    
    if not all(fields.values()):
        return strategy.redirect('accounts:login')  # Handle the error

    user = User.objects.create_user(
        email=fields['email'],
        first_name=fields['first_name'],
        last_name=fields['last_name'], # Default to empty string if not provided
    )
    return {
        'is_new': True,
        'user': user
    }

def activate_user(user, *args, **kwargs):
    user.is_active = True
    user.save()

def check_if_user_blocked(strategy, user, *args, **kwargs):
    if user.is_blocked:
        # Add an error message
        messages.error(strategy.request, "Your account is blocked. Please contact support.")
        return strategy.redirect('accounts:home')  # Redirect to an error page for blocked users

    return {
        'is_blocked': False,
        'user': user
    }
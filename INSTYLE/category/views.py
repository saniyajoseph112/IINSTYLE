from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from utils.decorators import admin_required

from .models import Category

# Create your views here.
@admin_required
def category_management(request):
    categories = Category.objects.all().order_by('id')
    return render(request, 'category_side/category_management.html', {'categories': categories})


@admin_required
def newcategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name').strip()

        if not category_name:
            messages.error(request,'category_name is required')
            return redirect('category:new_category')
        try:
            category = Category.objects.create(category_name=category_name)
            messages.success(request, f'Category "{category_name}" created successfully.')
            return redirect('category:category_management')
        except IntegrityError:
            messages.error(request, f'Category "{category_name}" already exists.')
        except Exception as e:
            messages.error(request, f'Failed to create category: {str(e)}')
        return render(request, 'category_side/new_category.html')

    return render(request, 'category_side/new_category.html') 



@admin_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category_name = request.POST.get('category_name').strip()
        slug = request.POST.get('slug')
        if not category_name:
            messages.error(request, 'Category name is required')
            return redirect('category:new_category')
        if Category.objects.filter(category_name=category_name).exclude(id=category_id).exists():
            messages.error(request, 'Category with this name already exists.')
            return redirect('category:new_category')
        else:
            category.category_name = category_name
            category.slug = slug
            category.save()
            messages.success(request, f'Category "{category_name}" updated successfully.')
            return redirect('category:category_management')
    return render(request, 'category_side/edit_category.html', {'category': category})

@admin_required
def category_is_available(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_available = not category.is_available
    category.save()
    messages.success(request, f'Category "{category.category_name}" availability updated.')
    return redirect('category:category_management')

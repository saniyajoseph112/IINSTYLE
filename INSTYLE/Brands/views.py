from django.shortcuts import get_object_or_404, render,redirect
from.models  import *
from utils.decorators import admin_required
from django.contrib import messages

@admin_required
def create(request):
    if request.method=='POST':
        brand_name=request.POST.get('brand_name')
        brand_image=request.FILES.get('brand_image')
        is_active=request.POST.get('is_active') == "on"

        if not brand_name:
            messages.error(request, 'Brand name is required.')
            return render(request, 'Brand_side/create.html')

        
        if Brand.objects.filter(brand_name__iexact=brand_name).exists():
            messages.error(request, 'Brand name already exists. Please choose a different name.')
            return render(request, 'Brand_side/create.html')


        if not brand_image:
            messages.error(request, 'Brand image is required.')
            return render(request, 'Brand_side/create.html')


        brand=Brand.objects.create(
            brand_name= brand_name,
            brand_image=brand_image,
            is_active=is_active
            )
        return redirect('Brands:list_brand')
    
    return render(request,'Brand_side/create.html')

@admin_required
def list_brand(request):
    brands=Brand.objects.all()
    return render(request,'Brand_side/list_brand.html',{'brands':brands})


@admin_required

def edit(request, pk):
    brand = get_object_or_404(Brand, id=pk)
    
    if request.method == 'POST':
        brand_name = request.POST.get('brand_name')
        brand_image = request.FILES.get('brand_image')
        is_active = request.POST.get('is_active') == "on"
    
        if not brand_name:
            messages.error(request, 'Brand name is required.')
            return render(request, 'Brand_side/edit.html', {'brands': brand})
        
        if Brand.objects.filter(brand_name__iexact=brand_name).exclude(id=pk).exists():
            messages.error(request, 'Brand name already exists. Please choose a different name.')
            return render(request, 'Brand_side/edit.html', {'brands': brand})
        
        
        if brand_image:
            brand.brand_image = brand_image

        
        brand.brand_name = brand_name
        brand.is_active = is_active
        brand.save()
        
        messages.success(request, 'Brand updated successfully.')
        return redirect('Brands:list_brand')
    
    return render(request, 'Brand_side/edit.html', {'brands': brand})

@admin_required
def delete(request,pk):
    brands=Brand.objects.get(id=pk)
    brands.is_active=not brands.is_active
    brands.save()
    return redirect('Brands:list_brand')


    
   



from django.shortcuts import render,redirect
from.models  import *

     
def create(request):
    if request.method=='POST':
        brand_name=request.POST.get('brand_name')
        brand_image=request.FILES.get('brand_image')
        is_active=request.POST.get('is_active') == "on"
        brand=Brand.objects.create(
            brand_name= brand_name,
            brand_image=brand_image,
            is_active=is_active
            )
        return redirect('Brands:list_brand')
    
    return render(request,'Brand_side/create.html')


def list_brand(request):
    brands=Brand.objects.all()
    return render(request,'Brand_side/list_brand.html',{'brands':brands})



def edit(request,pk):
    if request.method=='POST':
        brands=Brand.objects.get(id=pk)
        brands.brand_name=request.POST.get('brand_name')
        brands.brand_image=request.FILES.get('brand_image')
        brands.is_active=request.POST.get('is_active')
        brands.save()
        return redirect('Brands:list_brand')
    brands=Brand.objects.get(id=pk)
    return render(request,'Brand_side/edit.html',{'brands':brands})

def delete(request,pk):
    brands=Brand.objects.get(id=pk)
    brands.is_active=not brands.is_active
    brands.save()
    return redirect('Brands:list_brand')


    
   



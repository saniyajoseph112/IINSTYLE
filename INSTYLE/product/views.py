from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect
from.models import *
from category.models import *
from  Brands .models import *

# Create your views here.

def list_product(request):
    products=Products.objects.all().order_by('id')
    return render(request,'product_side/list_product.html', {'products':products})


def create(request):
    if request.method=='POST':
        product_name=request.POST.get('product_name')
        product_description=request.POST.get('product_description')
        product_category=request.POST.get('product_category')
        product_brand=request.POST.get('product_brand')
        price=request.POST.get('price')
        offer_price=request.POST.get('offer_price')
        thumbnail=request.FILES.get('thumbnail')
        is_active=request.POST.get('is_active') == "on"
        
        category=Category.objects.get(id=product_category)
        
        brand=Brand.objects.get(id=product_brand)
        

        product = Products.objects.create(
            product_name=product_name,
            product_description=product_description,
            product_category=category,
            product_brand=brand,
            price=price,
            offer_price=offer_price,
            thumbnail=thumbnail,
            is_active=is_active,
        )
        return redirect('product:list_product')
    categories=Category.objects.all()
    brands=Brand.objects.all()
    return render(request,'product_side/create_product.html',{'categories':categories,'brands':brands})


def edit(request,pk):
    product=Products.objects.get(id=pk)
    categories=Category.objects.all()
    brands=Brand.objects.all()
    if request.method=='POST':
        products=Products.objects.get(id=pk)

        product_category=request.POST.get('product_category')
        product_brand=request.POST.get('product_brand')
        products.product_name=request.POST.get('product_name')
        products.product_description=request.POST.get('product_description')
        products.price=request.POST.get('price')
        products.offer_price=request.POST.get('offer_price')
        products.is_active=request.POST.get('is_active') == "on"

        if 'thumbnail' in request.FILES:
            products.thumbnail = request.FILES['thumbnail']

        products.product_category = Category.objects.get(id=product_category) if product_category else None
        products.product_brand = Brand.objects.get(id=product_brand) if product_brand else None

        products.save()

        return redirect('product:list_product')
    
    return render(request,'product_side/edit_product.html',{'product':product,'categories':categories,'brands':brands})


def delete(request,pk):
    product=Products.objects.get(id=pk)
    product.is_active=not product.is_active
    product.save()
    pk=product.id
    return redirect('product:details',pk=pk)


def product_details(request,pk):
    products=Products.objects.get(id=pk) 
    images=ProductImage.objects.filter(product=products)
    varients=ProductVariant.objects.filter(product=products)
    return render(request, 'product_side/product_details.html' ,{'products':products, 'images':images,'varients':varients})   


def product_image(request,pk):
    if request.method =="POST":
        product=Products.objects.get(id=pk)
        images=request.FILES.getlist('images')

        for image in images:
            ProductImage.objects.create(product=product,images=image)
        
        return redirect('product:list_product')
    product = get_object_or_404(Products, id=pk)
    return render(request,'product_side/product_image.html',{'product':product})


def remove(request,pk):
    image=ProductImage.objects.get(id=pk)
    pk=image.product.id
    image.delete()
    return redirect('product:details',pk=pk)


def review(request,pk):
    product = get_object_or_404(Products, id=pk)
    pk=product.id
    if request.method=="POST":
        rating=request.POST.get('rating')
        review=request.POST.get('review')

        Review.objects.create(user=request.user,product=product,rating=rating,comment=review)

    return redirect('accounts:product_detailuser',pk=pk)


def list_varient(request,pk):
    product=Products.objects.get(id=pk)
    varients=ProductVariant.objects.filter(product=product)

    return render(request,'product_side/list_varient.html',{'varients':varients,'product':product}) 


def create_varient(request,pk):
    if request.method=="POST":
        products=Products.objects.get(id=pk)
        size=request.POST.get('size')
        stock=request.POST.get('variant_stock')
        status=request.POST.get('variant_status') == "on"

        # Check if the variant with the same size already exists for the product
        if ProductVariant.objects.filter(product=products, size=size).exists():
            messages.error(request, 'A variant with this size already exists for this product.')
            return render(request, 'product_side/create_varient.html', {'products': products})

        ProductVariant.objects.create(
            product=products,
            size=size,
            variant_stock=stock,
            variant_status=status,
        )
        pk=products.id
        return redirect('product:create_varient',pk=pk)
    products=Products.objects.get(id=pk)
    return render(request,'product_side/create_varient.html',{'products':products})

        
def edit_varient(request,pk):
    if request.method=="POST":
        varient=ProductVariant.objects.get(id=pk)
        varient.size=request.POST.get('size')
        varient.variant_stock=request.POST.get('variant_stock')
        varient.variant_status=request.POST.get('variant_status')== "on"
        varient.save()
        pk=varient.product.id
        return redirect('product:list_varient',pk=pk)

    varient=ProductVariant.objects.get(id=pk)
    return render(request,'product_side/edit_varient.html',{'varient':varient})


def delete_varient(request,pk):
    varient=ProductVariant.objects.get(id=pk)
    varient.variant_status=not varient.variant_status
    varient.save()
    pk=varient.product.id
    return redirect('product:list_varient',pk=pk)


    



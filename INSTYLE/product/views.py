from django.contrib import messages
from django.shortcuts import get_object_or_404, render,redirect
from.models import *
from category.models import *
from  Brands .models import *
from utils.decorators import admin_required

# Create your views here.
@admin_required
def list_product(request):
    products=Products.objects.all().order_by('id')
    return render(request,'product_side/list_product.html', {'products':products})

@admin_required
def create(request):
    if request.method == 'POST':
        # Fetching data from POST request
        product_name = request.POST.get('product_name').strip()
        product_description = request.POST.get('product_description').strip()
        product_category = request.POST.get('product_category')
        product_brand = request.POST.get('product_brand')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        thumbnail = request.FILES.get('thumbnail')
        is_active = request.POST.get('is_active') == "on"
        
        # Fetching related objects
        category = Category.objects.get(id=product_category)
        brand = Brand.objects.get(id=product_brand)

        # Validations
        if not product_name:
            messages.error(request, 'Product name is required.')
            return redirect('product:create')
        
        if Products.objects.filter(product_name__iexact=product_name).exists():
            messages.error(request, 'Product name already exists.')
            return redirect('product:create')
        
        if not product_category:
            messages.error(request, 'Product category is required.')
            return redirect('product:create')
        
        if not product_brand:
            messages.error(request, 'Product brand is required.')
            return redirect('product:create')
        
        if not price:
            messages.error(request, 'Price is required.')
            return redirect('product:create')
        
        if  offer_price > price:
            messages.error(request,'offer price must be lessthan price')
            return redirect('product:create')

        if int(price) > 1000000:
            messages.error(request,'price must be lessthan 1000000')
            return redirect('product:create')
        
        if not offer_price:
            messages.error(request, 'Offer price is required.')
            return redirect('product:create')
        
        if not product_description:
            messages.error(request,'product_description is required.')
            return redirect('product:create')

        # Creating the product
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
        messages.success(request, 'Product created successfully!')
        return redirect('product:list_product')
    
    # Get categories and brands for the form
    categories = Category.objects.all()
    brands = Brand.objects.all()

    return render(request, 'product_side/create_product.html', {
        'categories': categories,
        'brands': brands
    })

@admin_required
def edit(request, pk):
    product = Products.objects.get(id=pk)
    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == 'POST':
        product_category = request.POST.get('product_category')
        product_brand = request.POST.get('product_brand')
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        price = request.POST.get('price')
        offer_price = request.POST.get('offer_price')
        is_active = request.POST.get('is_active') == "on"

        # Validations
        if not product_name:
            messages.error(request, "Product name is required.")
        elif len(product_name) < 3:
            messages.error(request, "Product name must be at least 3 characters long.")
        if not price:
            messages.error(request, "Price is required.")
        elif not price.isdigit() or int(price) <= 0:
            messages.error(request, "Price must be a positive number.")
        if offer_price and (not offer_price.isdigit() or int(offer_price) >= int(price)):
            messages.error(request, "Offer price must be less than the regular price.")

        if messages.get_messages(request):
            return render(request, 'product_side/edit_product.html', {
                'product': product,
                'categories': categories,
                'brands': brands
            })

        # Update the product
        products = Products.objects.get(id=pk)
        products.product_name = product_name
        products.product_description = product_description
        products.price = int(price)
        products.offer_price = int(offer_price) if offer_price else None
        products.is_active = is_active

        if 'thumbnail' in request.FILES:
            products.thumbnail = request.FILES['thumbnail']

        products.product_category = Category.objects.get(id=product_category) if product_category else None
        products.product_brand = Brand.objects.get(id=product_brand) if product_brand else None

        products.save()
        messages.success(request, 'Product Created Successfully')
        return redirect('product:list_product')

    return render(request, 'product_side/edit_product.html', {
        'product': product,
        'categories': categories,
        'brands': brands
    })

@admin_required
def delete(request,pk):
    product=Products.objects.get(id=pk)
    product.is_active=not product.is_active
    product.save()
    pk=product.id
    messages.success(request, 'Status Upadated Successfully')
    return redirect('product:details',pk=pk)

@admin_required
def product_details(request,pk):
    products=Products.objects.get(id=pk) 
    images=ProductImage.objects.filter(product=products)
    varients=ProductVariant.objects.filter(product=products)
    return render(request, 'product_side/product_details.html' ,{'products':products, 'images':images,'varients':varients})   

@admin_required
def product_image(request,pk):
    if request.method =="POST":
        product=Products.objects.get(id=pk)
        images=request.FILES.getlist('images')

        for image in images:
            ProductImage.objects.create(product=product,images=image)
        messages.success(request, 'Product Image Added Successfully')
        return redirect('product:list_product')
    product = get_object_or_404(Products, id=pk)
    return render(request,'product_side/product_image.html',{'product':product})

@admin_required
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

@admin_required
def list_varient(request,pk):
    product=Products.objects.get(id=pk)
    varients=ProductVariant.objects.filter(product=product)

    return render(request,'product_side/list_varient.html',{'varients':varients,'product':product}) 

@admin_required
def create_varient(request, pk):
    products = Products.objects.get(id=pk)

    if request.method == "POST":
        size = request.POST.get('size').strip()
        stock = request.POST.get('variant_stock').strip()
        status = request.POST.get('variant_status') == "on"

        if not size:
            messages.error(request, 'Size is required.')
        if not stock:
            messages.error(request, 'Stock is required.')
        elif not stock.isdigit() or int(stock) < 0:
            messages.error(request, 'Stock must be a non-negative number.')

        if size and ProductVariant.objects.filter(product=products, size=size).exists():
            messages.error(request, 'A variant with this size already exists for this product.')

        if messages.get_messages(request):
            return render(request, 'product_side/create_varient.html', {'products': products})


        ProductVariant.objects.create(
            product=products,
            size=size,
            variant_stock=int(stock),
            variant_status=status,
        )
        messages.success(request, 'Variant Created Successfully')
        return redirect('product:create_varient', pk=products.id)

    return render(request, 'product_side/create_varient.html', {'products': products})


@admin_required       
def edit_varient(request, pk):
    varient = ProductVariant.objects.get(id=pk)

    if request.method == "POST":
        size = request.POST.get('size').strip()
        variant_stock = request.POST.get('variant_stock').strip()
        variant_status = request.POST.get('variant_status') == "on"

        if not size:
            messages.error(request, 'Size is required.')
        if not variant_stock:
            messages.error(request, 'Stock is required.')
        elif not variant_stock.isdigit() or int(variant_stock) < 0:
            messages.error(request, 'Stock must be a non-negative number.')

        if messages.get_messages(request):
            return render(request, 'product_side/edit_varient.html', {'varient': varient})

        varient.size = size
        varient.variant_stock = int(variant_stock)
        varient.variant_status = variant_status
        varient.save()
        messages.success(request, 'Variant Edited Successfully')
        return redirect('product:list_varient', pk=varient.product.id)

    return render(request, 'product_side/edit_varient.html', {'varient': varient})


def delete_varient(request,pk):
    varient=ProductVariant.objects.get(id=pk)
    varient.variant_status=not varient.variant_status
    varient.save()
    pk=varient.product.id
    messages.success(request, 'Status Upadated Successfully')
    return redirect('product:list_varient',pk=pk)


    



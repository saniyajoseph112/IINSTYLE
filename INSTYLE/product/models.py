from django.db import models
from category.models import Category
from Brands.models import Brand
from accounts.models import User



class Products(models.Model):
    product_name = models.CharField( max_length=50,null = False)
    product_description = models.TextField(max_length=5000, null=False)
    product_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    product_brand = models.ForeignKey(Brand,on_delete=models.SET_NULL, null=True)
    price =models.DecimalField( max_digits=10, decimal_places=2)
    offer_price = models.DecimalField( max_digits=10, decimal_places=2)
    thumbnail = models.ImageField(upload_to='thumbnail_images',null=True)

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def percentage_discount(self):
        return int(((self.price - self.offer_price) / self.price) * 100)
        
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0
    
    def __str__(self):
        return f"{self.product_brand.brand_name}-{self.product_name}"
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size =models.CharField(max_length=10,null=True)
    variant_stock = models.PositiveIntegerField(null=False,default=0)
    variant_status = models.BooleanField(default=True)




class ProductImage(models.Model):
    product = models.ForeignKey("Products", on_delete=models.CASCADE,null=True )
    images = models.ImageField(upload_to="product_images")

    def __str__(self):
        return f"Image for {self.product.product_name}"

    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.CharField( max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)    
    
    def str(self):
        return f'{self.user} - {self.product}'
    
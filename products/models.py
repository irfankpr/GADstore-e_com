from django.contrib.postgres.fields import ArrayField
from django.db import models


# Create your models here.

class categories(models.Model):
    category_name = models.CharField(max_length=500, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category_image = models.ImageField(upload_to='products/category_images', blank=False)
    offer = models.BooleanField(default=False)
    offer_tittle = models.CharField(max_length=100, null=True)
    offer_rate = models.FloatField(null=True)
    maxlimit = models.FloatField(null=True)


class sub_categories(models.Model):
    sub_cat_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    parent_cat = models.ForeignKey(categories, on_delete=models.CASCADE)


class products(models.Model):
    Product_name = models.CharField(max_length=300, blank=False, unique=True)
    slug = models.SlugField(blank=False)
    products_desc = models.TextField()
    products_dyl = models.TextField(blank=False)
    MRP = models.FloatField()
    price = models.FloatField()
    thumbnail = models.ImageField(upload_to='products/products_images', blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    available_stock = models.BigIntegerField()
    category = models.ForeignKey(categories, on_delete=models.CASCADE, null=True)
    sub_category = ArrayField(models.CharField(max_length=100), null=True)
    Offer = models.BooleanField(default=False)
    Dis = models.FloatField(default=0)
    Disrate = models.FloatField(default=0)


class prodtct_image(models.Model):
    prodtct_name = models.ForeignKey(products, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/products_images', blank=False)

from django.db import models
from products.models import products, categories
from profiles.models import userprofiles, address


# Create your models here.


class Coupons(models.Model):
    Coupon_code = models.CharField(max_length=100, unique=True)
    minimum = models.FloatField(default=0)
    maxlimit = models.FloatField(default=0)
    discount_rate = models.FloatField(default=0)
    discount_type = models.CharField(max_length=50, default='FLAT', choices=(('FLAT', 'FLAT'), ('UPTO', 'UPTO')))


class orders(models.Model):
    product = models.ForeignKey(products, on_delete=models.SET_NULL,null=True)
    user = models.ForeignKey(userprofiles, on_delete=models.SET_NULL, null=True)
    address = models.TextField(null=True)
    quantity = models.IntegerField()
    Total = models.FloatField()
    payment = models.CharField(max_length=100, default='COD')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')
    payment_id = models.CharField(max_length=500, null=True)
    Offer_applied = models.TextField( null=True)
    coupon_applied = models.TextField(null=True)
    discount_price = models.FloatField(default=0)
    delivered_date = models.DateTimeField(null=True)

from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

import products.models


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, phone, email, password=None):
        if not email:
            raise ValueError('email required')
        if not phone:
            raise ValueError('phone required')
        user = self.model(
            email=self.normalize_email(email),
            phone=phone,
            ref_id=first_name + last_name + phone[:4],
            first_name=first_name,
            last_name=last_name,
            wallet=0,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email, first_name, last_name, password, ):
        user = self.create_user(
            email=self.normalize_email(email),
            phone=phone,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save()
        return user


class userprofiles(AbstractBaseUser):
    username = None
    phone = models.CharField(('phone number'), max_length=15, unique=True)
    email = models.EmailField(blank=False, unique=True, max_length=100)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    ref_id = models.CharField(max_length=300, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    wallet = models.FloatField(null=True)
    people = models.IntegerField(default=0)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', ]

    objects = MyAccountManager()

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class cart(models.Model):
    user_id = models.ForeignKey(userprofiles, blank=False, on_delete=models.CASCADE, unique=False)
    product_id = models.ForeignKey(products.models.products, on_delete=models.CASCADE, blank=False, )
    count = models.IntegerField(default=1)
    total = models.BigIntegerField(default=0)
    discount = models.FloatField(default=0)


class address(models.Model):
    user = models.ForeignKey(userprofiles, blank=False, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50, blank=False)
    phone = models.CharField(max_length=15, blank=False)
    postal_PIN = models.CharField(max_length=20, blank=False)
    address = models.TextField(blank=False)


class walletTrans(models.Model):
    user = models.ForeignKey(userprofiles, blank=False, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.FloatField(default=0)
    CrDr = models.CharField(max_length=20, choices=(('Credited', 'Credited'), ('Debited', 'Debited')))
    desc = models.TextField()

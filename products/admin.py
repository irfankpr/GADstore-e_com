from django.contrib import admin
from products.models import categories,products,prodtct_image
from django.contrib.auth.admin import UserAdmin

# Register your models here.

admin.site.register(categories)
admin.site.register(products)
admin.site.register(prodtct_image)
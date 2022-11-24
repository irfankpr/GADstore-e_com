from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from admins import views

urlpatterns = [
    path('admin/', views.index,name='admin'),
    path('admin/login', views.login),
    path('admin/logout', views.log_out,name='admin-logout'),
    path('admin/home', views.adminhome, name='adminhome'),
    path('admin/category', views.category, name='category'),
    path('admin/products', views.adm_products, name='adminproducts'),
    path('admin/addproduct', views.addproduct, name='addproduct'),
    path('admin/delete-product/<int:id>/', views.deleteproduct, name='delete-product'),
    path('admin/product_dtl/<int:pid>/', views.product_dtl, name="product_dtl"),
    path('admin/users', views.users, name="users"),
    path('admin/block-users/<int:bid>/', views.block_users, name="block-user"),
    path('product-up', views.product_up, name="product-up"),
    path('admin/catedit/<int:cid>/', views.cat_edit, name="catedit"),
    path('cat-up', views.cat_up, name="cat-up"),
    path('sub-up', views.sub_up, name="sub-up"),
    path('admin/orders', views.order, name="allorders"),
    path('admin/Coupons', views.Couponspage, name="Coupons"),
    path('admin/addcoupons', views.addcoupon, name="addcoupon"),
    path('admin/delete-coupon/<int:id>/', views.dlt_coupon, name="delete-coupon"),
    path('admin/Offers', views.Offers, name="cat-Offers"),
    path('admin/Offers', views.Offers, name="prd-Offers"),
    path('admin/addoffer', views.addoffers, name="addoffer"),
    path('admin/add-product-offer', views.addPoffers, name="add-product-offer"),
    path('admin/dlt-offer', views.dlt_offer, name="dlt-offer"),
    path('admin/down-exel', views.download, name="down-exel"),
    path('admin/report', views.report, name="report"),
    path('admin/down-rep', views.down_report, name="down-rep"),

]

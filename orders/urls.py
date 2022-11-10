from django.urls import path, include

from orders import views

# ...........................users . urls
urlpatterns = [
    path('checkout', views.chkout,name='chkout'),
    path('place-order', views.place_order,name='place-order'),
    path('order-up', views.order_up, name='order-up'),
    path('cancel-order/<int:id>/', views.cancel_order, name='cancel-order'),
    path('return-order/<int:id>/', views.return_order, name='return-order'),
    path('apply-coupon', views.applycoupon, name='apply-coupon'),

]

from django.urls import path, include

from users import views

# ...........................users . urls
urlpatterns = [
    path('', views.index, name='index'),
    path('sign', views.sign, name='sign'),
    path('signin', views.signin),
    path('log', views.log, name="log"),
    path('logotp', views.loginotp),
    path('login-psw', views.login),
    path('home', views.home, name='home'),
    path('shop', views.shop, name='shop'),
    path('cartv', views.cartv, name='cartv'),
    path('detail/<int:id>', views.dtl, name='detail'),
    path('login-otp', views.loginotp),
    path('usr-logout', views.usr_logout),
    path('landing', views.landing, name='landing'),
    path('my-orders', views.myorders, name='my-orders'),
    path('cshop', views.cshop, name='cshop'),
    path('my-wallet', views.wallet, name='my-wallet'),
    path('my-wallet/<int:id>', views.Generateinvoice, name='invoice'),
]

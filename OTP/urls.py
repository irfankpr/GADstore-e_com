

from django.urls import path, include
from OTP import views

urlpatterns = [
                  path('otp', views.otp,name='otp'),
                  path('verify-otp', views.loginotp),
                    path('resendotp', views.reotp,name='resendotp'),

              ]

from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from profiles.models import userprofiles
from twilio.rest import Client
import random

import profiles.models


# Create your views here.
class otpgen():
    Otp = 0
    phone = 0

    def send_otp(phone):
        account_ssid = 'ACe6367b4e0523f007dac124700c291ac2'
        auth_token = 'ACe6367b4e0523f007dac124700c291ac2'
        target_number = '+91' + phone
        print(phone)
        twilio_number = '+19035679739'
        otp = random.randint(1000, 9999)
        otpgen.Otp = str(otp)
        otpgen.phone = phone
        msg = 'GADstore account verification otp is ' + str(otp)
        client = Client(account_ssid, auth_token)
        message = client.messages.create(
            body=msg,
            from_=twilio_number,
            to=target_number,
        )
        print(message.body)
        return True


@never_cache
def otp(request):
    return render(request, 'otp.html', {'phone': otpgen.phone})


def loginotp(request):
    obj = otpgen()
    if request.method == "POST":
        Rotp = request.POST['otp']
        Gotp = obj.Otp
        if Rotp == Gotp:
            user = userprofiles.objects.get(phone=obj.phone)
            login(request, user)
            return JsonResponse({'valid': True})
        else:
            return JsonResponse({'invalid': True})
    else:
        messages.error(request, 'Something went wrong, please try again')
        return redirect('otp')


def reotp(request):
    phone = request.GET.get('phone')
    otpgen.send_otp(phone)
    return JsonResponse({'sent': True})

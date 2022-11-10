from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, logout
from profiles.models import userprofiles, cart, address
from django.shortcuts import render


# Create your views here.
@login_required(login_url='/')
@never_cache
def myprofile(request):
    id = request.user.id
    user = userprofiles.objects.get(id=id)
    add = address.objects.filter(user_id=id)
    return render(request, 'profile.html', {'user': user, 'address': add})


@login_required(login_url='/')
def newaddress(request):
    if request.method == 'POST':
        id = request.user.id
        name = request.POST['name']
        Phone = request.POST['Phone']
        pin = request.POST['pin']
        add = request.POST['addressarea']
        obj = address()
        print(id, name, Phone, pin, add)
        obj.user_id = id
        obj.full_name = name
        obj.phone = Phone
        obj.postal_PIN = pin
        obj.address = add
        obj.save()
        print(request.META.get('HTTP_REFERER'))
        return redirect(request.META.get('HTTP_REFERER'))


@never_cache
def dltaddress(request, id):
    address.objects.filter(id=id).delete()
    return redirect('my-profile')


@login_required(login_url='/')
@never_cache
def password(request):
    usr=userprofiles.objects.get(id=request.user.id)
    return render(request, 'password.html',{'usr':usr})


@login_required(login_url='/')
@never_cache
def passupdate(request):
    if request.method=='POST':
        old = request.POST['old']
        new1 = request.POST['new1']
        new2 = request.POST['new2']
        newenc=make_password(new1)
        if new1 == new2:
            usr=authenticate(request, phone=request.user.phone, password=old)
            if usr:
                userprofiles.objects.filter(id=request.user.id).update(password=newenc)
                messages.error(request, 'Password updated.')
                return redirect('my-profile')
        else:
            messages.error(request, 'Password confirmation failed !')
            return redirect('password')

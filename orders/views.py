import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import F
from products.models import products, categories
from orders.models import orders
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from profiles.models import cart, address,userprofiles,walletTrans
from orders.models import Coupons


# Create your views here.
@never_cache
def chkout(request):
    if not request.user.is_authenticated:
        return  redirect('log')
    items = cart.objects.filter(user_id_id=request.user.id)
    total = 0
    add = address.objects.filter(user_id=request.user.id)
    coup = Coupons.objects.all()
    for i in items:
        total = total + i.total
    return render(request, 'checkout.html', {'items': items, 'ttl': total, 'address': add, 'coupons': coup})


@login_required(login_url='/')
@never_cache
def place_order(request):
    if not 'add_id' in request.POST:
        return JsonResponse({'placed': False})
    if request.POST['paym'] == 'COD':
        citems = cart.objects.filter(user_id_id=request.user.id)
        add_id = request.POST['add_id']
        add = address.objects.get(id=add_id)
        for c in citems:
            Dis = 0
            coupdis = None
            offer = None
            if c.product_id.Offer:
                prd = products.objects.get(id=c.product_id_id)
                offer = "Product offer by :  " + str(prd.Disrate) + " %  , Total off on this order :  " + str(int(
                    (c.total * prd.Disrate) / 100))
            elif c.product_id.category.offer:
                cat = categories.objects.get(id=c.product_id.category_id)
                offer = "Category offer by :  " + str(cat.offer_rate) + " %  , Total off on this order :  " + str(int(
                    (c.total * cat.offer_rate) / 100))
            ordrADD = add.full_name + ", " + add.phone + ", " + add.postal_PIN + ", " + add.address
            if request.POST.get('coupon'):
                coupon = Coupons.objects.get(Coupon_code=request.POST['coupon'])
                Dis = (c.total * coupon.discount_rate) / 100
                if Dis > coupon.maxlimit:
                    Dis = coupon.maxlimit
                coupdis = coupon.Coupon_code + " :-  discount rate of  " + str(
                    coupon.discount_rate) + "  for minimum purchase  " + str(
                    coupon.minimum) + "  with maxlimit of  " + str(coupon.maxlimit)
            orders(user=c.user_id, product=c.product_id, coupon_applied=coupdis, quantity=c.count, status='Placed',
                   Total=c.total - Dis, address=ordrADD, payment='COD', discount_price=Dis, Offer_applied=offer).save()
        cart.objects.filter(user_id_id=request.user.id).delete()
        return JsonResponse({'Placed': True})
    elif request.POST['paym'] == 'razorpay':
        citems = cart.objects.filter(user_id_id=request.user.id)
        add_id = request.POST['add_id']
        payment_id = request.POST['payment_id']
        add = address.objects.get(id=add_id)
        for c in citems:
            Dis = 0
            coupdis = None
            offer = None
            if c.product_id.Offer:
                prd = products.objects.get(id=c.product_id_id)
                offer = "Product offer by :  " + str(prd.Disrate) + " %  , Total off on this order :  " + str(int(
                    (c.total * prd.Disrate) / 100))
            elif c.product_id.category.offer:
                cat = categories.objects.get(id=c.product_id.category_id)
                offer = "Category offer by :  " + str(cat.offer_rate) + " %  , Total off on this order :  " + str(int(
                    (c.total * cat.offer_rate) / 100))
            ordrADD = add.full_name + ", " + add.phone + ", " + add.postal_PIN + ", " + add.address
            if request.POST.get('coupon'):
                coupon = Coupons.objects.get(Coupon_code=request.POST['coupon'])
                Dis = (c.total * coupon.discount_rate) / 100
                if Dis > coupon.maxlimit:
                    Dis = coupon.maxlimit
                coupdis = coupon.Coupon_code + " :-  discount rate of  " + str(
                    coupon.discount_rate) + "  for minimum purchase  " + str(
                    coupon.minimum) + "  with maxlimit of  " + str(coupon.maxlimit)
            orders(user=c.user_id, product=c.product_id, coupon_applied=coupdis, quantity=c.count, status='Placed',
                   Total=c.total - Dis, address=ordrADD, payment='Razorpay', payment_id=payment_id, discount_price=Dis,
                   Offer_applied=offer).save()

            products.objects.filter(id=c.product_id_id).update(available_stock=F('available_stock') - c.count)
        cart.objects.filter(user_id_id=request.user.id).delete()
        return JsonResponse({'Placed': True})


@login_required(login_url='/')
def order_up(request):
    if request.method == 'POST':
        stt = request.POST['status']
        ord = request.POST['order']
        o = orders.objects.get(id=ord)
        if stt == "Delivered":
            o.delivered_date = datetime.datetime.now()
        if stt == "Cancelled":
            products.obects.filter(id=o.product_id).update(available_stock=F('available_stock') + o.quantity)
            if o.payment != "COD":
                usr = userprofiles.objects.get(id=request.user.id)
                usr.wallet = usr.wallet + o.Total
                usr.save()
                walletTrans(user=request.user, quantity=o.Total,
                            desc="Refunded for cancel of : " + o.product.Product_name).save()
        if stt == "Refunded":
            usr = userprofiles.objects.get(id=request.user.id)
            usr.wallet = usr.wallet + o.Total
            usr.save()
            walletTrans(user=request.user, quantity=o.Total,
                        desc="Refunded for return of : " + o.product.Product_name).save()

        o.status = stt
        o.save()
        return JsonResponse({'ordered': True})


@login_required(login_url='/')
def cancel_order(request, id):
    o = orders.objects.get(id=id)
    if o.payment != "COD":
        o.status= "Cancelled"
        o.save()
        usr = userprofiles.objects.get(id=request.user.id)
        usr.wallet = usr.wallet + o.Total
        usr.save()
        walletTrans(user=request.user,quantity=o.Total,desc="Refunded for cancel of : "+o.product.Product_name).save()
    else:
        o.status = "Cancelled"
        o.save()
    return redirect('my-orders')


@login_required(login_url='/')
def return_order(request, id):
    o = orders.objects.get(id=id)
    o.status = "Returned"
    o.save()
    return redirect('my-orders')


def applycoupon(request):
    try:
        if request.method == 'GET':
            if 'code' in request.GET:
                code = request.GET['code']
                if Coupons.objects.filter(Coupon_code=code).exists():
                    coupon = Coupons.objects.get(Coupon_code=code)
                    crt = cart.objects.filter(user_id_id=request.user.id)
                    tottal = 0
                    for c in crt:
                        tottal = tottal + c.total
                    if tottal < coupon.minimum:
                        limit = 'This coupon needs minimum purchase of ₹ ' + str(coupon.minimum)
                        return JsonResponse({'limit': limit})
                    else:
                        Tdis = 0
                        for c in crt:
                            Dis = (c.total * coupon.discount_rate) / 100
                            Tdis = Tdis + Dis
                            c.discount = round(Dis, 2)
                            c.save()
                        offer = 'You have got  ' + str(coupon.discount_rate) + ' % OFF'
                        return JsonResponse({'offer': offer, 'Tdis': Tdis, 'ttl': tottal - Tdis})
                else:
                    return JsonResponse({'invalid': True})
            else:
                return JsonResponse({'nocode': True})

    except:
        pass

import datetime
from ast import literal_eval
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string, get_template
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import auth
from orders.models import orders
from profiles.models import userprofiles, cart, walletTrans
from OTP.views import otpgen
from products.models import categories, products, sub_categories, prodtct_image
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger

from users.utils import render_to_pdf


# Create your views here.


@never_cache
def index(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin')
        else:
            return redirect('/home')
    else:
        return redirect('landing')


# signup module
def signin(request):
    if request.method == 'POST':
        if request.POST['Fname'] and request.POST['Sname'] and request.POST['Password1'] and request.POST[
            'Password2'] and request.POST['email'] and request.POST['phone']:
            Fname = request.POST['Fname']
            Sname = request.POST['Sname']
            passw1 = request.POST['Password1']
            passw2 = request.POST['Password2']
            email = request.POST['email']
            phone = request.POST['phone']
            if userprofiles.objects.filter(phone=phone).exists():
                messages.error(request, 'Phone already exist')
                return redirect('/sign')
            if userprofiles.objects.filter(email=email).exists():
                messages.error(request, 'e-mail already exist')
                return redirect('/sign')
            if passw2 == passw1:
                if request.POST.get("refid"):
                    refid = request.POST['refid']
                    ref = userprofiles.objects.filter(ref_id=refid)
                    if ref:
                        userprofiles.objects.filter(ref_id=refid).update(wallet=F('wallet') + 50,
                                                                         people=F('people') + 1)
                        refr = userprofiles.objects.get(ref_id=refid)
                        walletTrans(quantity=50, CrDr='Credited', desc='For reffering - ' + Fname + " " + Sname,
                                    user=refr).save()

                    else:
                        messages.error(request, 'Invalid refferal id')
                        return redirect('/sign')

                usr = userprofiles.objects.create_user(first_name=Fname, last_name=Sname,
                                                       password=passw1, email=email,
                                                       phone=phone)
                usr.save()
                print("user sign inned successfully")
                auth.login(request, usr)
                res = redirect('/home')
                if 'gust_cart' in request.COOKIES:
                    ck = literal_eval(request.COOKIES['gust_cart'])
                    for p in ck:
                        prd = products.objects.get(id=int(p))

                        ttl = prd.price * ck[p]
                        cart(user_id=usr, product_id=prd, count=ck[p], total=ttl, discount=0).save()
                        res.delete_cookie('gust_cart')

                res.set_cookie('user_id', usr.id)
                return res
            else:
                print("password confirmation failed")
                messages.error(request, 'Password confirmation failed ')
                return redirect('/sign')
        else:
            messages.error(request, 'you cannot submit without credentials filled !')
            return redirect('/sign')
    else:
        return redirect('/sign')


def login(request):
    if request.method == 'POST':
        if request.POST['phone'] and request.POST['Password']:
            Phone = request.POST['phone']
            password = request.POST['Password']
            usr = authenticate(request, phone=Phone, password=password, is_admin=False)
            print(usr)
            if usr:
                user = userprofiles.objects.get(phone=Phone)
                if usr:
                    if user.blocked:
                        messages.error(request, 'You are restricted by admin')
                        return redirect('/log')
                auth.login(request, user)
                res = redirect('/home')
                user = userprofiles.objects.get(phone=Phone)
                res.set_cookie('user_id', user.id)
                if 'gust_cart' in request.COOKIES:
                    ck = literal_eval(request.COOKIES['gust_cart'])
                    for p in ck:
                        try:
                            prd = products.objects.get(id=int(p))
                            ttl = prd.price * ck[p]
                            ss = cart.objects.filter(user_id=user, product_id=prd, ).exists()
                            if not ss:
                                cart(user_id=user, product_id=prd, count=ck[p], total=ttl, discount=0).save()
                        except:
                            pass
                        res.delete_cookie('gust_cart')
                return res
            else:
                messages.error(request, 'Invalid credentials.')
                return redirect('/log')
        else:
            messages.error(request, 'you cannot submit without credentials filled !')
            return redirect('/log')
    else:
        return redirect('/log')


def loginotp(request):
    if request.method == "GET" and request.GET['phone']:
        phone = request.GET['phone']
        otpgen.send_otp(request,phone)
        messages.error(request, 'OTP sent to ' + phone)
        return render(request, 'otp.html', {'phone': phone})
    else:
        messages.error(request, 'enter phone number')
        return redirect('log')

def usr_logout(request):
    logout(request)
    return redirect('/')



@never_cache
def sign(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'User-Signin.html')


@never_cache
def log(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'User-Login.html')


@login_required(login_url='/')
@never_cache
def home(request):
    if request.user.is_authenticated:
        if request.user.is_authenticated:
            count = cart.objects.filter(user_id=request.user.id).count()
        elif 'gust_cart' in request.COOKIES:
            c = literal_eval(request.COOKIES['gust_cart'])
            count = len(c)
        else:
            count = 0
        new = products.objects.all().order_by('-added_date')[:12]
        cat = categories.objects.all().annotate(cat_count=Count('category_name')).order_by('category_name')
        rndm = products.objects.all().order_by('?')[:8]
        for c in cat:
            c.prds = products.objects.filter(category=c.id).count()
        subcat = sub_categories.objects.all().annotate(subcat_count=Count('sub_cat_name')).order_by('sub_cat_name')
        return render(request, 'index.html', {'cat': cat, 'new': new, 'subcat': subcat, 'count': count, "sug":rndm})
    else:
        messages.error(request, 'Something went wrong, please try again')
        return redirect('/log')


@never_cache
def shop(request):
    if request.method == 'GET':
        if 'key' in request.GET:
            key = request.GET['key']
            q = Q()
            q &= Q(Product_name__icontains=key) | Q(products_dyl__icontains=key) | Q(products_desc__icontains=key) | Q(
                category__category_name__icontains=key)
            prds = products.objects.filter(q)
            if request.user.is_authenticated:
                count = cart.objects.filter(user_id=request.user.id).count()
            elif 'gust_cart' in request.COOKIES:
                c = literal_eval(request.COOKIES['gust_cart'])
                count = len(c)
            else:
                count = 0
            cat = categories.objects.all().annotate(cat_count=Count('category_name')).order_by('category_name')
            subcat = sub_categories.objects.all().annotate(subcat_count=Count('sub_cat_name')).order_by('sub_cat_name')
            paging = Paginator(prds, 12)
            page = request.GET.get('page')
            paged = paging.get_page(page)
            prd_count = prds.count()
            return render(request, 'shop.html',
                          {'products': paged, 'prd_count': prd_count, 'key': key, 'cat': cat, 'subcat': subcat,
                           'count': count})


        else:
            if request.user.is_authenticated:
                count = cart.objects.filter(user_id=request.user.id).count()
            elif 'gust_cart' in request.COOKIES:
                c = literal_eval(request.COOKIES['gust_cart'])
                count = len(c)
            else:
                count = 0
            cat = categories.objects.all().annotate(cat_count=Count('category_name')).order_by('category_name')
            subcat = sub_categories.objects.all().annotate(subcat_count=Count('sub_cat_name')).order_by('sub_cat_name')
            prds = products.objects.filter()
            paging = Paginator(prds, 12)
            page = request.GET.get('page')
            paged = paging.get_page(page)
            prd_count = prds.count()
            return render(request, 'shop.html',
                          {'products': paged, 'prd_count': prd_count, 'key': '', 'cat': cat, 'subcat': subcat,
                           'count': count})


@never_cache
def cshop(request):
    if request.method == 'GET':
        if request.GET['key']:
            key = request.GET['key']
            q = Q()
            q &= Q(Product_name__icontains=key) | Q(products_dyl__icontains=key) | Q(products_desc__icontains=key)
            prds = products.objects.filter(q)
            if request.user.is_authenticated:
                count = cart.objects.filter(user_id=request.user.id).count()
            elif 'gust_cart' in request.COOKIES:
                c = literal_eval(request.COOKIES['gust_cart'])
                count = len(c)
            else:
                count = 0
            cat = categories.objects.all().annotate(cat_count=Count('category_name')).order_by('category_name')
            subcat = sub_categories.objects.all().annotate(subcat_count=Count('sub_cat_name')).order_by('sub_cat_name')
            html = render_to_string('shop.html',
                                    {'products': prds, 'key': key, 'cat': cat, 'subcat': subcat, 'count': count})
            return HttpResponse(html)


@never_cache
def cartv(request):
    if request.user.is_authenticated:
        crt = cart.objects.filter(user_id=request.user.id).order_by('product_id')
    else:
        crt = []
        if 'gust_cart' in request.COOKIES:
            c = request.COOKIES['gust_cart']
            c = literal_eval(c)
            for i in c.keys():
                p = products.objects.get(id=i)
                count = c[i]
                t = (p.price - p.Dis) * count
                crt.append({p: [count, t]})
    return render(request, 'cart.html', {'cart': crt})


@never_cache
def dtl(request, id):
    count = cart.objects.filter(user_id=request.user.id).count()
    prd = products.objects.filter(id=id)
    d = products.objects.get(id=id)
    like = products.objects.filter(category_id=d.category_id)[:7]
    images = prodtct_image.objects.filter(prodtct_name_id=id)
    return render(request, 'detail.html', {'product': prd, 'count': count, 'Like': like, 'images': images})


@never_cache
def landing(request):
    if 'gust_cart' in request.COOKIES:
        c = literal_eval(request.COOKIES['gust_cart'])
        count = len(c)
    else:
        count = 0
    new = products.objects.all().order_by('-added_date')[:12]
    cat = categories.objects.all().annotate(cat_count=Count('category_name')).order_by('category_name')
    subcat = sub_categories.objects.all().annotate(subcat_count=Count('sub_cat_name')).order_by('sub_cat_name')
    rndm = products.objects.all().order_by('?')[:8]
    return render(request, 'gadstore.html', {'cat': cat, 'new': new, 'subcat': subcat, 'count': count, "sug":rndm})


@never_cache
@login_required(login_url='/')
def myorders(request):
    o = orders.objects.filter(user_id=request.user.id).order_by('-date')
    paging = Paginator(o, 10)
    page = request.GET.get('page')
    paged = paging.get_page(page)
    prd_count = o.count()
    return render(request, 'my-orders.html', {'orders': paged,'prd_count': prd_count, })


@never_cache
@login_required(login_url='/')
def wallet(request):
    if request.user.is_admin == False:
        trans = walletTrans.objects.filter(user=request.user).order_by('-date')
        count = cart.objects.filter(user_id=request.user.id).count()
        return render(request, 'wallet.html', {'count': count, 'trans': trans})


def Generateinvoice(request, id):
    ord = orders.objects.get(id=id)
    template = get_template('admin/invoice_template.html')
    data = {
        'today': datetime.date.today(),
        'order': ord,
    }
    html = template.render(data)
    pdf = render_to_pdf('admin/invoice_template.html', data)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "invoice_template.html_%s.pdf " % ('12341231')
        content = "inline; filename='%s'" % (filename)

        download = request.GET.get('download')
        if download:
            content = "attachment; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse(pdf, content_type='application/pdf')


def fil_sort(request):
    key = request.GET["key"]
    frm = request.GET["from"]
    to = request.GET['to']
    sort = request.GET['sort']
    q = Q()
    q &= Q(Product_name__icontains=key) | Q(products_dyl__icontains=key) | Q(products_desc__icontains=key)
    if sort == "HL":
        prds = products.objects.filter(q).order_by('-price')
    elif sort == "LH":
        prds = products.objects.filter(q).order_by('price')
    else:
        prds = products.objects.filter(q).order_by('-price')

    if frm == "~" and to == "~":
        prds=prds
    elif frm != "~" and to == "~":
        prds = prds.filter(price__gte=int(frm))
    elif frm != "~" and to != "~":
        prds = prds.filter(price__gte=int(frm), price__lte=int(to))

    return render(request,"Components/filter.html",{"products":prds})

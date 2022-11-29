import calendar
import datetime
import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum, F, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import auth
from orders.models import orders, Coupons
from profiles.models import userprofiles, cart
from products.models import categories, products, sub_categories, prodtct_image
from django.views.generic import View
import os
from admins.utils import render_to_pdf  # created in step 4


@never_cache
def index(request):
    if request.user.is_authenticated:
        return redirect('adminhome')
    else:
        return render(request, 'admin/admin-login.html')


def login(request):
    if request.method == 'POST':
        if request.POST['phone'] and request.POST['Password']:
            Phone = request.POST['phone']
            password = request.POST['Password']
            print(Phone, password)
            usr = authenticate(request, phone=Phone, password=password,is_staff=True, is_admin=True)
            if usr is not None and usr.is_admin == True:
                auth.login(request, usr)
                res = redirect('adminhome')
                user = userprofiles.objects.get(phone=Phone)
                res.set_cookie('username', user.first_name + usr.last_name)
                res.set_cookie('password', password)
                request.session['username'] = user.first_name + usr.last_name
                request.session['password'] = password
                print("res")
                return res

            else:
                messages.error(request, 'Invalid credentials.')
                return redirect('/admin')
        else:
            messages.error(request, 'you cannot submit without credentials filled !')
            return redirect('/admin')
    else:
        return redirect('/admin')


def log_out(request):
    logout(request)
    return redirect('admin')


def addproduct(request):
    if request.method == "POST":
        if request.POST['name'] and request.POST['mrp'] and request.POST['hilights'] and request.POST['count'] and \
                request.POST['price'] and request.POST['desc'] and request.FILES['thumb'] and request.POST['cat']:
            prod = products()
            prod.Product_name = request.POST["name"]
            prod.slug = slugify(prod.Product_name)
            prod.products_dyl = request.POST["hilights"]
            prod.products_desc = request.POST["desc"]
            prod.MRP = request.POST["mrp"]
            prod.price = request.POST["price"]
            prod.thumbnail = request.FILES['thumb']
            prod.available_stock = request.POST["count"]
            prod.category_id = request.POST["cat"]
            ex = products.objects.filter(Product_name=request.POST["name"]).exists()
            if ex:
                messages.error(request, 'Product named :- ' + prod.Product_name + ' already exists.')
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                prod.save()
            prd = products.objects.get(Product_name=prod.Product_name)
            if 'pimages' in request.FILES:
                images = request.FILES.getlist('pimages')
                for i in images:
                    sv = prodtct_image()
                    sv.image = i
                    print(i)
                    sv.prodtct_name = prd
                    sv.save()

            messages.error(request, 'New product ' + prod.Product_name + ' added.', extra_tags='added.')
            return redirect('adminproducts')


        else:
            messages.error(request, 'you cannot submit without credentials filled !', extra_tags='added.')
            return redirect('addproduct')


def product_up(request):
    if request.method == 'POST':
        pid = request.POST['pid']
        pname = request.POST['pname']
        obj = products.objects.get(id=pid)
        thumb = obj.thumbnail
        obj.Product_name = request.POST['pname']
        obj.slug = slugify(pname)
        obj.products_dyl = request.POST['hilights']
        obj.products_desc = request.POST['desc']
        obj.MRP = request.POST['mrp']
        obj.available_stock = request.POST['stock']
        obj.price = request.POST['price']
        obj.category = categories.objects.get(id=request.POST['cat'])
        if 'thumbnail' in request:
            obj.thumbnail = request.FILES['thumbnail']
        else:
            obj.thumbnail = thumb
        obj.save()
        messages.error(request, 'Product updated')
        return redirect('admin/product_dtl/' + pid)


def deleteproduct(request, id):
    if request.method == 'GET':
        pr = products.objects.get(id=id)
        name = pr.Product_name
        try:
            os.remove('media/'+str(pr.thumbnail))
        except:
            pass
        images=prodtct_image.objects.filter(prodtct_name=pr)
        try :
            for i in images:
                os.remove('media/' + str(i.image))
        except:
            pass
        pr.delete()
        cart.objects.filter(product_id=id).delete()
        messages.error(request, 'Product ' + name + ' deleted.', extra_tags='dlt')
        return redirect('adminproducts')


@login_required(login_url='admin')
@never_cache
def product_dtl(request, pid):
    prd = products.objects.get(id=pid)
    cat = categories.objects.all()
    sub = sub_categories.objects.all()
    return render(request, "admin/product-edit.html", {'prd': prd, 'cat': cat, 'sub': sub})


@login_required(login_url='admin')
@never_cache
def adminhome(request):
    if request.user.is_authenticated:
        admins = userprofiles.objects.filter(is_staff=True)
        p = products.objects.filter(available_stock__lte=10)

        # daily Product sales report graph
        today = datetime.datetime.now()
        dates = orders.objects.filter(date__month=today.month).values('date__date').annotate(
            orders=Count('id')).order_by('date__date')
        returns = orders.objects.filter(date__month=today.month).values('date__date').annotate(
            returns=Count('id', filter=Q(status='Cancelled'))).order_by(
            'date__date')
        sales = orders.objects.filter(date__month=today.month).values('date__date').annotate(
            sales=Count('id', filter=Q(status='Delivered'))).order_by(
            'date__date')
        todayords = orders.objects.filter(date__date=today).annotate(rev=Sum('Total'))
        # monthly sales
        months = orders.objects.values('date__date__month').annotate(
            sales=Sum('Total', filter=Q(status='Delivered'))).order_by('-date__date__month')[:6]

        last30 = orders.objects.filter().values('date__date').annotate(
            orders=Count('id')).order_by('-date__date')[:6]

        Top = orders.objects.filter(date__range=(today - datetime.timedelta(days=30), today)).annotate(prd=Max('Total'))

        rev12 = orders.objects.all().values('date__date__month').annotate(
            rev=Sum('Total'),).order_by('date__date__month')[:12]
        R12=0
        for r in rev12:
            R12 = R12 + r.get("rev")

        return render(request, 'admin/admin-dashbord.html',
                      {'admins': admins, 'products': p, 'dates': dates, 'returns': returns, 'sales': sales,
                       'today': today.date,"rev12":rev12,"R12":R12,
                       'todayords': todayords, 'months': months, 'last30': last30, 'Top': Top})
    else:
        return redirect('admin')


@login_required(login_url='/')
@never_cache
def category(request):
    cat = categories.objects.all()
    return render(request, 'admin/Category.html', {'cat': cat})


@login_required(login_url='admin')
@never_cache
def adm_products(request):
    if request.method == "GET":

        cat = categories.objects.all()
        if 'key' in request.GET:
            q = Q(Product_name__icontains=request.GET.get('key')) | Q(
                category__category_name__icontains=request.GET.get('key'))
            product = products.objects.filter(q)
            paging = Paginator(product, 12)
            page = request.GET.get('page')
            paged = paging.get_page(page)
            prd_count = product.count()
            p = render(request, 'admin/products.html', {'product': product, 'cat': cat, 'key': request.GET.get('key'),'products': paged, 'prd_count': prd_count,})
            return p
        else:
            product = products.objects.filter()
            paging = Paginator(product, 12)
            page = request.GET.get('page')
            paged = paging.get_page(page)
            prd_count = product.count()
            p = render(request,  'admin/products.html', {'product': product, 'cat': cat, 'products': paged, 'prd_count': prd_count,})
            return p


@login_required(login_url='admin')
@never_cache
def users(request):
    usr = userprofiles.objects.exclude(is_admin=True).order_by('id')
    paging = Paginator(usr, 5)
    page = request.GET.get('page')
    paged = paging.get_page(page)
    prd_count = usr.count()
    return render(request, 'admin/users.html', {'user': paged,'count': prd_count})


@login_required(login_url='admin')
@never_cache
def block_users(request, bid):
    usr = userprofiles.objects.get(id=bid)
    if usr.blocked:
        print(bid)
        usr.blocked = False
        usr.save()
    else:
        usr.blocked = True
        usr.save()
    print(usr.blocked)
    return redirect(users)



@never_cache
def cat_edit(request, cid):
    cat = categories.objects.filter(id=cid)
    sub = sub_categories.objects.filter(parent_cat_id=cid)
    return render(request, 'admin/category-edit.html', {'cat': cat, "sub": sub})


def cat_up(request):
    if request.method == "POST":
        id = request.POST['cid']
        obj = categories.objects.get(id=id)
        obj.category_name = request.POST['cname']
        obj.description = request.POST['desc']
        if 'catimg' in request.FILES:
            obj.category_image = request.FILES['catimg']
        obj.save()
        messages.error(request, 'Category updated ')
        return redirect('admin/catedit/' + id)


def sub_up(request):
    id = request.POST['sid']
    sub_categories.objects.get(id=id).delete()
    messages.error(request, 'Sub-category deleted')
    return redirect('category')


@login_required(login_url='/')
@never_cache
def order(request):
    ord = orders.objects.all().order_by('-date')
    paging = Paginator(ord, 10)
    page = request.GET.get('page')
    paged = paging.get_page(page)
    prd_count = ord.count()
    return render(request, 'admin/orders.html', {'orders': paged,'count': prd_count,})


@login_required(login_url='/')
@never_cache
def Couponspage(request):
    coupons = Coupons.objects.all()
    return render(request, 'admin/Coupons.html', {'coupons': coupons})


@login_required(login_url='/')
def addcoupon(request):
    if request.method == 'POST':
        if Coupons.objects.filter(Coupon_code=request.POST['code']).exists():
            messages.error(request, 'Coupon code alredy exists !')
            return redirect('Coupons')
        Coupons.objects.create(Coupon_code=request.POST['code'],
                               minimum=request.POST['min'],
                               maxlimit=request.POST['limit'],
                               discount_rate=request.POST['rate'],
                               )
    return redirect('Coupons')


def dlt_coupon(request, id):
    if request.method == "GET":
        Coupons.objects.filter(id=id).delete()
        return redirect('Coupons')


@never_cache
def Offers(request):
    if request.method == "GET":
        cat = categories.objects.all()
        off = categories.objects.filter(offer=True)
        return render(request, 'admin/Offers.html', {'offers': off, 'cat': cat})

@never_cache
def POffers(request):
    if request.method == "GET":
        off = products.objects.filter(Offer=True)
        return render(request, 'admin/Poffer.html', {'offers': off, })


def addoffers(request):
    if request.method == "POST":
        id = request.POST['cat']
        cat = categories.objects.get(id=id)
        cat.offer = True
        cat.offer_tittle = request.POST['tittle']
        rate = request.POST['rate']
        cat.offer_rate = rate
        cat.maxlimit = request.POST['limit']
        cat.save()
        products.objects.filter(category_id=id).update(Dis=((F('MRP') * rate) / 100))
        messages.error(request, 'New offer added')
        return redirect('cat-Offers')


def addPoffers(request):
    if request.method == "POST":
        id = request.POST['product']
        prd = products.objects.get(id=id)
        prd.Offer = True
        offer = int(request.POST['Offer'])
        prd.Disrate = offer
        prd.Dis = int((prd.MRP * offer) / 100)
        prd.save()
        messages.error(request, 'New offer added')
        return redirect('prd-Offers')


def dlt_offer(request):
    if request.method == "GET":
        id = request.GET.get('id')
        print(id)
        if request.GET.get('off') == 'prd':
            prd = products.objects.get(id=id)
            prd.Offer = False
            if prd.category.offer == True:
                prd.Dis= (prd.MRP*prd.category.offer_rate)*100
            else:
                prd.Dis = 0
            prd.Disrate = 0
            prd.save()
        elif request.GET.get('off') == 'cat':
            cat = categories.objects.get(id=id)
            cat.offer = False
            cat.offer_rate = 0
            cat.offer_tittle = None
            cat.maxlimit = 0
            products.objects.filter(category=cat).update(Dis=0)
            cat.save()
        return redirect(request.META.get('HTTP_REFERER'))


def download(request):
    if request.method == "GET":
        if request.GET['type'] == 'PDF':
            return GeneratePdf(request)
        elif request.GET['type'] == 'XLS':
            return download_excel_data(request)
    else:
        return redirect(request.META.get('HTTP_REFERER'))


def download_excel_data(request):
    try:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="sales_report.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sales report')  # this will make a sheet named Users Data

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['No', 'Product', 'Mrp', 'Price', 'Discount_price', 'Final_price', 'Quantity', 'Total',
                   'Payment', 'Payment_id', 'Coupon_applied', "Offer_applies", 'Customer_name', 'Customer_phone',
                   'Customer_e-mail', 'Address', 'Order_date',
                   'Deliver_date', 'Order_status', ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
            ws.col(col_num).width = 6000  # at 0 row 0 column

        font_style = xlwt.XFStyle()
        month = request.GET['month']
        year = request.GET['year']
        if year == "":
            m = month.split("-")[1]
            y = month.split("-")[0]
            rows = orders.objects.filter(date__date__year=y, date__date__month=m).order_by('date')
        elif month == "":
            rows = orders.objects.filter(date__date__year=year).order_by('date')

        for o in rows:
            row_num += 1
            ws.write(row_num, 0, row_num, font_style)
            try:
                ws.write(row_num, 1, o.product.Product_name, font_style)
            except:
                ws.write(row_num, 1, "deleted product", font_style)
            try:
                ws.write(row_num, 2, o.product.MRP, font_style)
            except:
                ws.write(row_num, 2, "---", font_style)
            try:
                ws.write(row_num, 3, o.product.price, font_style)
            except:
                ws.write(row_num, 3, "---", font_style)
            try:
                ws.write(row_num, 4, int(o.product.Dis), font_style)
            except:
                ws.write(row_num, 4, "---", font_style)
            try:
                ws.write(row_num, 5, o.product.price - int(o.product.Dis), font_style)
            except:
                ws.write(row_num, 5, "---", font_style)
            ws.write(row_num, 6, o.quantity, font_style)
            ws.write(row_num, 7, o.Total, font_style)
            ws.write(row_num, 8, o.payment, font_style)
            ws.write(row_num, 9, o.payment_id, font_style)
            ws.write(row_num, 10, o.coupon_applied, font_style)
            ws.write(row_num, 11, o.Offer_applied, font_style)
            ws.write(row_num, 12, o.user.first_name + " " + o.user.last_name, font_style)
            ws.write(row_num, 13, o.user.phone, font_style)
            ws.write(row_num, 14, o.user.email, font_style)
            ws.write(row_num, 15, o.address, font_style)
            ws.write(row_num, 16, str(o.date), font_style)
            if o.delivered_date is None:
                Ddate = o.status
            else:
                Ddate = o.delivered_date.replace(tzinfo=None)
            ws.write(row_num, 17, Ddate, font_style)
            ws.write(row_num, 18, o.status, font_style)

        wb.save(response)

        return response
    except:
        messages.error(request, 'something went wrong try again')
        return redirect(request.META.get('HTTP_REFERER'))


def GeneratePdf(request):
    month = request.GET['month']
    year = request.GET['year']
    if year=="":
        m=month.split("-")[1]
        y=month.split("-")[0]
        range = year+" - "+ calendar.month_name[int(m)]
        ord = orders.objects.filter(date__date__year=y,date__date__month=m).order_by('date')
        prdc = orders.objects.filter(date__date__year=y,date__date__month=m).annotate(
            sales=Sum('Total', filter=Q(status='Delivered'))).order_by(
            'date__date')
    elif month=="":
        range="year "+str(year)
        ord = orders.objects.filter(date__date__year=year).order_by('date')
        prdc = orders.objects.filter(date__date__year=year).values('product_id').annotate(
            sales=Sum('Total', filter=Q(status='Delivered'))).order_by(
            'date__date')


    template = get_template('admin/sales_rep.html')
    data = {
        'today': datetime.date.today(),
        'orders': ord,
        'range': range,
        'prdc': prdc,
    }
    html = template.render(data)
    pdf = render_to_pdf('admin/sales_rep.html', data)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "sales_rep.html_%s.pdf " % ('12341231')
        content = "inline; filename='%s'" % (filename)

        download = request.GET.get('download')
        if download:
            content = "attachment; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse(pdf, content_type='application/pdf')


@never_cache
def report(request):
    if request.user.is_admin:
        if 'type' in request.GET:
            type=request.GET['type']
            From = request.GET['fDate']
            to = request.GET['tDate']
            data = orders.objects.filter(date__range=(From, to)).values('date__date__'+type).annotate(
                rev=Sum('Total'),
                orders=Count('id'),
                sold=Count('id', Q(status="Delivered")),
                cancel=Count('id', Q(status="Cancelled")),
                returnd=Count('id', Q(status="Refunded")),
            ).order_by('date__date__'+type)


            return render(request,"admin/report.html",{"data":data, "chk":type, "frm":From, "to":to})
        else:
            data = orders.objects.all().values('date__date__month').annotate(
                rev=Sum('Total'),
                orders=Count('id'),
                sold=Count('id', Q(status="Delivered")),
                cancel=Count('id', Q(status="Cancelled")),
                returnd=Count('id', Q(status="Refunded")),
            ).order_by('date__date__month')[:12]
            return render(request,"admin/report.html",{"data":data})

    else:
        return redirect("/")



def down_report(request):
    type = request.GET["type"]
    f =request.GET["from"]
    t = request.GET["to"]
    print(type)
    return JsonResponse({'Placed': True})


@never_cache
def analytics(request):
    e = datetime.date.today().year
    s = 2020
    years=[]
    for y in range(s, e + 1):
        years.append(y)
    data = orders.objects.filter(date__date__month=datetime.date.today().month).order_by("date__date")

    return render(request,"admin/analytics.html",{"year":years,"orders":data})
@never_cache
def report_table(request):
    if request.GET["type"]=="month":
        val = request.GET["month"]
        month = val.split("-", 1)[1]
        print(month)
        year = val.split("-",1)[0]
        print(year)
        data = orders.objects.filter(date__date__year=year,date__date__month=month).order_by("date__date")

    if request.GET["type"]=="year":
        year = request.GET["year"]
        data = orders.objects.filter(date__date__year=year).order_by("date__date")
        print(year)
    print(data)
    return render(request,'Components/report_table.html',{"orders":data})

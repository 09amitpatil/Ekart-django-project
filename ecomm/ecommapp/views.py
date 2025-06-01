from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from ecommapp.models import Product, Cart, Order
import random
import razorpay
from django.db.models import Q
from django.core.mail import send_mail
import ast


def products(request):
    # fetch data from product table for is_active=true
    p = Product.objects.filter(is_active=True)
    context = {}
    context['data'] = p
    return render(request, 'index.html', context)


def viewcart(request):
    c = Cart.objects.filter(userid=request.user.id)
    sum = 0
    for x in c:
        sum = sum+x.pid.price*x.qty

    context = {}
    context['data'] = c
    context['total'] = sum
    context['n'] = len(c)
    return render(request, 'cart.html', context)


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def user_login(request):
    uid = request.user.id
    print("logeed user id :", uid)

    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        name = request.POST['uname']
        upass = request.POST['upass']
        u = authenticate(username=name, password=upass)
        # print(u)
        if u is not None:
            login(request, u)
            return redirect('/products')
        else:
            context = {}
            context['errmsg'] = 'Invalid username or password'
            return render(request, 'login.html', context)


def user_logout(request):
    logout(request)
    return redirect('/login')


def register(request):
    context = {}
    if request.method == "GET":
        return render(request, 'register.html')
    else:
        n = request.POST['uname']
        p = request.POST['upass']
        cp = request.POST['ucpass']
        if n == '' or p == '' or cp == '':
            context['errmsg'] = 'Fields cannot be Empty !!'
            return render(request, 'register.html', context)
        elif p != cp:
            context['errmsg'] = 'Password and confirm password dosennot match'
            return render(request, 'register.html', context)
        elif len(p) < 8:
            context['errmsg'] = 'Password must be more than 8 characters'
            return render(request, 'register.html', context)
        else:
            try:
                u = User.objects.create(username=n, email=n, password=p)
                u.set_password(p)
                u.save()
                context['success'] = "User created Successfully "
                return render(request, 'register.html', context)
            except Exception:
                context['errmsg'] = 'User with same username already exists , Please Login'
                return render(request, 'register.html', context)


# category filter

def catfilter(request, cv):
    print(cv)
    # select * from ecommapp_product where cat=cv and is_active=true;
    q1 = Q(is_active=True)
    q2 = Q(cat=cv)
    p = Product.objects.filter(q1 & q2)
    # print(p)
    context = {}
    context['data'] = p
    return render(request, 'index.html', context)

# sorting


def sortprice(request, sv):
    if sv == '1':
        t = '-price'
    else:
        t = 'price'

    p = Product.objects.order_by(t).filter(is_active=True)
    context = {}
    context['data'] = p
    return render(request, 'index.html', context)

# price filter


def pricefilter(request):
    min = request.GET['min']
    max = request.GET['max']
    # print(min)
    # print(max)
    q1 = Q(price__gte=min)
    q2 = Q(price__lte=max)
    p = Product.objects.filter(q1 & q2)
    context = {}
    context['data'] = p
    return render(request, 'index.html', context)


def product_details(request, pid):
    p = Product.objects.filter(id=pid)
    context = {}
    context['data'] = p
    return render(request, 'product_details.html', context)


def cart(request, pid):
    if request.user.is_authenticated:
        u = User.objects.filter(id=request.user.id)
        p = Product.objects.filter(id=pid)
        # check product exist or not
        q1 = Q(userid=u[0])
        q2 = Q(pid=p[0])
        c = Cart.objects.filter(q1 & q2)
        n = len(c)
        context = {}
        context['data'] = p
        if n == 1:
            context['msg'] = 'product already exists in cart'
        else:
            c = Cart.objects.create(userid=u[0], pid=p[0])
            c.save()
            context['success'] = "Product added successfully to cart!!"

        return render(request, 'product_details.html', context)
    else:
        return redirect('/login')


def updateqty(request, x, cid):
    c = Cart.objects.filter(id=cid)
    q = c[0].qty
    if x == '1':
        q = q+1
    elif q > 1:
        q = q-1
    c.update(qty=q)
    return redirect('/viewcart')


def removecart(requeat, cid):
    c = Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')


def removeorder(requeat, cid):
    c = Order.objects.filter(id=cid)
    c.delete()
    return redirect('/fetchorder')


def place_order(request):
    c = Cart.objects.filter(userid=request.user.id)
    orderid = random.randrange(1000, 9999)
    print(orderid)
    for x in c:
        amount = x.qty*x.pid.price
        o = Order.objects.create(
            orderid=orderid, qty=x.qty, pid=x.pid, userid=x.userid, amt=amount)
        o.save()
        x.delete()
    return redirect('/fetchorder')


def fetchorderdetails(request):
    orders = Order.objects.filter(userid=request.user.id)
    # print(orders)
    sum = 0
    for x in orders:
        sum = sum+x.amt

    context = {}
    context['orders'] = orders
    context['tamount'] = sum
    context['n'] = len(orders)
    return render(request, 'place_order.html', context)


def makepayment(request):
    client = razorpay.Client(
        auth=("rzp_test_mIUw7uMpA6TIwg", "OCi5gZt4NY4y9BxweughTZae"))
    orders = Order.objects.filter(userid=request.user.id)
    sum = 0
    for x in orders:
        sum = sum+x.amt
        oid = x.orderid

    data = {"amount": sum*100, "currency": "INR", "receipt": oid}
    payment = client.order.create(data=data)
    print(payment)
    context = {}
    context['payment'] = payment
    context['amount'] = sum
    return render(request, 'pay.html', context)


def paymentsuccess(request):
    sub = "Ekart-Order status"
    client = razorpay.Client(
        auth=("rzp_test_mIUw7uMpA6TIwg", "OCi5gZt4NY4y9BxweughTZae"))
    orders = Order.objects.filter(userid=request.user.id)
    sum = 0
    oid = None
    for x in orders:
        sum += x.amt
        oid = x.orderid

    data = {"amount": sum, "currency": "INR", "receipt": oid}
    payment = client.order.create(data=data)
    msg = f"Thank you for shopping \n"
    msg += f"Order details:\n"
    msg += f"Order_id:{payment['id']}\n"
    msg += f"Amount: {payment['amount']}\n"
    msg += f"Receipt: {payment['receipt']}\n"
    msg += f"Order_status: {payment['status']}\n"

    sub = "Ekart-Order status"
    frm = "er.patilamit@gmail.com"
    u = User.objects.get(id=request.user.id)
    to = u.email
    send_mail(sub, msg, frm, [to], fail_silently=False)

    return render(request, 'paymentsuccess.html')

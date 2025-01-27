from django.contrib import admin
from django.urls import path
from ecommapp import views
from django.conf import settings
from django.conf.urls.static import static
# from ecommapp.views import Contactform

urlpatterns = [
    path('products', views.products),
    path('product_details', views.product_details),
    path('viewcart', views.viewcart),
    path('about', views.about),
    path('contact', views.contact),
    path('place_order', views.place_order),
    path('login', views.user_login),
    path('logout', views.user_logout),
    path('register', views.register),
    path('catfilter/<cv>', views.catfilter),
    path('sort/<sv>', views.sortprice),
    path('pricefilter', views.pricefilter),
    path('product_details/<pid>', views.product_details),
    path('addcart/<pid>', views.cart),
    path('updateqty/<x>/<cid>', views.updateqty),
    path('removecart/<cid>',views.removecart),
    path('fetchorder', views.fetchorderdetails),
    path('makepayment', views.makepayment),
    path('removeorder/<cid>',views.removeorder),
    path('paymentsuccess',views.paymentsuccess),



]

if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

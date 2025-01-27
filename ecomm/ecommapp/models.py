from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Product(models.Model):
    CAT = ((1, 'Mobile'), (2, 'Shoes'), (3, 'Cloths'))
    name = models.CharField(max_length=50)
    price = models.FloatField()
    cat = models.IntegerField(verbose_name='category', choices=CAT)
    pdetails = models.CharField(max_length=100, verbose_name='product_details')
    is_active = models.BooleanField(default=True)
    pimage = models.ImageField(upload_to="image")

    def __str__(self):

        return self.name


class Cart(models.Model):
    pid = models.ForeignKey('product', on_delete=models.CASCADE, db_column='pid')
    userid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='userid')
    qty=models.IntegerField(default=1)


class Order(models.Model):
    orderid=models.CharField(max_length=50)
    pid = models.ForeignKey('product', on_delete=models.CASCADE, db_column='pid')
    userid = models.ForeignKey('auth.user', on_delete=models.CASCADE, db_column='userid')
    qty=models.IntegerField(default=1)
    amt=models.FloatField(default=0)
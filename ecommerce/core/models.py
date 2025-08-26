from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField

class customer(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE)
    phone_field = models.CharField(max_length=12)

    def __str__(self):
        return self.user.username

class category(models.Model):
    category_name = models.CharField(max_length=200)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    desc = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_avl_count = models.IntegerField(default=0)
    img = models.ImageField(upload_to='img/')

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price
    
    def get_final_price(self):
        return self.get_total_price()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('OrderItem')
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    order_id = models.CharField(max_length=100, unique=True, default=None, blank=True, null=True)
    datetime_ofpayment = models.DateTimeField(default=timezone.now)  
    order_delivered = models.BooleanField(default=False)
    order_received = models.BooleanField(default=False)
    
    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.datetime_ofpayment and self.id:
            self.order_id = self.datetime_ofpayment.strftime('PAY2ME%Y%M%dODR') + str(self.id)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_count(self):
        order = Order.objects.get(pk=self.pk)
        return order.items.count() 
    
class CheckoutAddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip_code = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


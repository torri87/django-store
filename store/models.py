from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=255, unique=True)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=255, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-time_created', 'name']


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'В очікуванні'
        PAID = 'PAID', 'Оплачений'
        SHIPPED = 'SHIPPED', 'Відправлений'
        DELIVERED = 'DELIVERED', 'Доставлений'

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Замовлення: {self.id} від {self.user.username}"

    class Meta:
        ordering = ['-time_created']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} шт. - {self.product.name}"
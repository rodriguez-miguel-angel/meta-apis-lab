from django.db import models

from django.contrib.auth.models import User

from datetime import datetime, date

# Create your models here.
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return f"[[Category]] slug: {self.slug}. title: {self.title}."

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"[[MenuItem]] title: {self.title}. price: {self.price}. featured: {self.featured}. category: {self.category}."
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
      
    def __str__(self) -> str:
        return f"[[Cart]] quantity: {self.quantity}. unit_price: {self.unit_price}."
    
    class Meta:
        unique_together = ('menu_item', 'user')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)

    def __str__(self) -> str:
        return f"[[Order]] status: {self.status}. date: {self.date}."

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
      
    def __str__(self) -> str:
        return f"[[OrderItem]] quantity: {self.quantity}. unit_price: {self.unit_price}."
    
    class Meta:
        unique_together = ('order', 'menu_item')
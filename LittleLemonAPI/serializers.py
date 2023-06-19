from rest_framework import serializers

from rest_framework.validators import UniqueTogetherValidator 
from django.contrib.auth.models import User 

from .models import Category, MenuItem, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    """
    version-00:
    category = CategorySerializer()
    """
    """
    version-01:
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['user','id', 'title', 'price', 'featured', 'category', 'category_id']
        validators = [
            UniqueTogetherValidator(
                queryset=MenuItem.objects.all(),
                fields=['user', 'id', 'title', 'price', 'featured', 'category', 'category_id']
            ) 
        ]
        extra_kwargs = {
            "price" : {
                "min_value" : 0,
            },
        }

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    menu_item_id = serializers.IntegerField(write_only=True)
    menu_item = MenuItemSerializer(read_only=True)

    """
    version-01:
    unit_price = serializers.SerializerMethodField(method_name='get_unit_price')
    version-02:
    """
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menu_item.price', read_only=True)
    price = serializers.SerializerMethodField(method_name='get_price')

    class Meta:
        model = Cart
        fields = ['user','id','quantity', 'unit_price', 'price', 'menu_item', 'menu_item_id']
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=['user','id','quantity', 'unit_price', 'price', 'menu_item', 'menu_item_id']
            ) 
        ]
        extra_kwargs = {
            "quantity" : {
                "min_value" : 0,
            },
            "unit_price" : {
                "min_value" : 0,
                "read_only" : True,
            },
            "price" : {
                "min_value" : 0,
                "read_only" : True,
            },
        }
    """
    version-01:
    def get_unit_price(self, product:Cart):
        return product.menu_item.price
      
    """
    """
    version-01:
    def get_price(self, product:Cart):
        return product.quantity * product.menu_item.price

    version-02:
    def get__price(self, obj):
        return obj.quantity * obj.menu_item.price
    """
    def get_price(self, product:Cart):
        return product.quantity * product.menu_item.price
    

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    delivery_crew = serializers.RelatedField(
        queryset=User.objects.all(), 
    )
    class Meta:
        model = Order
        fields = ['user','delivery_crew','status', 'total', 'date']
        validators = [
            UniqueTogetherValidator(
                queryset=Order.objects.all(),
                fields=['user','delivery_crew','status', 'total', 'date']
            ) 
        ]
        extra_kwargs = {
            "total" : {
                "min_value" : 0,
            },
        }

class OrderItemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    order_id = serializers.IntegerField(write_only=True)
    order = OrderSerializer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)
    menu_item = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['user','id','quantity', 'unit_price', 'price', 'order', 'order_id', 'menu_item', 'menu_item_id']
        validators = [
            UniqueTogetherValidator(
                queryset=OrderItem.objects.all(),
                fields=['user','id','quantity', 'unit_price', 'price', 'order', 'order_id', 'menu_item', 'menu_item_id']
            ) 
        ]
        extra_kwargs = {
            "quantity" : {
                "min_value" : 0,
            },
            "unit_price" : {
                "min_value" : 0,
            },
            "price" : {
                "min_value" : 0,
            },
        }

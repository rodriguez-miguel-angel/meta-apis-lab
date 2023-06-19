from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser

from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle 

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from django.http import HttpResponse, JsonResponse

from rest_framework import status

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer 

from django.forms.models import model_to_dict

from datetime import datetime, date
import logging

import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
"""
MenuItems Endpoints:

Role:
    - Manager
Purpose:
    - GET. Lists all menu items
    - POST. Creates a new menu item and returns 201 - Created

Role:
    - Customer, Delivery Crew
Purpose:
    - Get. Lists all menu items. Return a 200 – Ok HTTP status code.

"""
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    ordering_fields = ['price', 'title']
    filterset_fields = ['price', 'title']
    search_fields = ['category__title','title']

    def post(self, request):
        if request.user.groups.filter(name='Manager').exists():
            new_item = MenuItem()
            payload = self.request.data
            new_item.title = payload['title']
            new_item.price = payload['price']
            new_item.featured = payload['featured']
            new_item.category = Category.objects.get(pk=payload['category_id'])
            new_item.save()
            return Response({"message":"201 - Created."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        
    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        elif(self.request.method=='POST'):
            """
            version-00 [insecure]:
            return []
            """
            """
            version-01 [secure]:
            return [IsAuthenticated()]
            """
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]


"""
MenuItems Endpoints:

Role:
    - Manager
Purpose:
    - GET. Lists single menu item
    - PUT/PATCH. Updates single menu item
    - DELETE. Deletes menu item

Role:
    - Customer, Delivery Crew
Purpose:
    - Get. Lists single menu item.

"""
class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def put(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            payload = self.request.data
            modified_menu_item = MenuItem.objects.get(pk=pk)
            modified_menu_item.title = payload['title']
            modified_menu_item.price = payload['price']
            modified_menu_item.featured = payload['featured']
            modified_menu_item.category = Category.objects.get(pk=payload['category_id'])
            modified_menu_item.save()
            return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            payload = self.request.data
            modified_menu_item = MenuItem.objects.get(pk=pk)

            if 'title' in payload:
                modified_menu_item.title = payload['title']
            if 'price' in payload:
                modified_menu_item.price = payload['price']
            if 'featured' in payload:
                modified_menu_item.featured = payload['featured']
            if 'category_id' in payload:
                modified_menu_item.category = Category.objects.get(pk=payload['category_id'])
            modified_menu_item.save()

            return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            menu_item = MenuItem.objects.filter(pk=pk)
            if menu_item:
                menu_item.delete()
                return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"404 - Not found."}, status=status.HTTP_404_NOT_FOUND)    
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)


    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        elif(self.request.method in ['PUT', 'PATCH', 'DELETE']):
            return [IsAuthenticated()]
        else:
            return [IsAuthenticatedOrReadOnly()]


"""
[[Cart Management Endpoints: /api/cart/menu-items]]

Role:
    - Customer

Purpose: 
    - GET. Returns current items in the cart for the current user token
    - POST. Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items
    - DELETE. Deletes all menu items created by the current user token
"""
class CartView(generics.ListAPIView, generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)

    def post(self, request):
        if request.auth == None:
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        token = Token.objects.filter(user=user)
        if token:
            new_cart = Cart()
            payload = self.request.data
            new_cart.user = user
            new_cart.menu_item = MenuItem.objects.get(pk=payload['menu_item_id'])
            new_cart.quantity = payload['quantity']
            """
            version-01:
            new_cart.unit_price = payload['unit_price']
            new_cart.price = payload['price']
            """
            """
            version-02:
            """
            new_cart.unit_price = new_cart.menu_item.price
            new_cart.price = new_cart.menu_item.price * new_cart.quantity
            new_cart.save()
            print(new_cart)
            return Response({"message":"201 - Created."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request):
        if request.auth == None:
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        token = Token.objects.filter(user=user)
        if token:
            cart = Cart.objects.all().filter(user=self.request.user)
            cart.delete()
            return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        if(self.request.method in ['GET', 'POST', 'DELETE']):
            return [IsAuthenticated()]
        return [IsAuthenticated()]


"""
Order Management Endpoint: 
    - /api/orders

Role:
    - Customer

Purpose: 
    - GET. Returns all orders with order items created by this user.
    - POST. Creates a new order item for the current user. 
        Gets current cart items from the cart endpoints and adds those items to the order items table. 
        Then deletes all items from the cart for this user.

Role:
    - Manager

Purpose: 
    - GET. Returns all orders with order items by all users

Role:
    - Delivery Crew

Purpose:    
    - GET. Returns all orders with order items assigned to the delivery crew
"""
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    
    ordering_fields = ['status', 'total']
    filterset_fields = ['status', 'total']
    search_fields = ['status','date']    

    def get_queryset(self):
        return Order.objects.all().filter(user=self.request.user)

    def get(self, request):
        if request.user.groups.filter(name='Manager').exists():
            print("manager")
            orders = Order.objects.all().values()
            list_of_orders = []
            for order in orders:
                list_of_orders.append(order)
            context = {
                "message":"200 - OK.",
                "data": list_of_orders
            }
            return Response(context, status=status.HTTP_200_OK)
        elif request.user.groups.filter(name='Delivery crew').exists():
            print("delivery crew")
            
            orders = Order.objects.all().values()
            list_of_orders = []
            for order in orders:
                if order['delivery_crew_id'] != None:
                    list_of_orders.append(order)
            context = {
                "message":"200 - OK.",
                "data": list_of_orders
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            user = request.user
            token = Token.objects.filter(user=user)
            if token:
                print("customer")
                order = Order.objects.all().filter(user=user).values()
                context = {
                    "message":"200 - OK.",
                    "data": order
                }
                return Response(context, status=status.HTTP_200_OK)
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if request.auth == None:
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery crew').exists():
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        token = Token.objects.filter(user=user)
        if token:
            new_order = Order()
            new_order.user = user

            payload = self.request.data
            
            new_order.total = 0
            #  It must be in YYYY-MM-DD format.
            new_order.date = payload['date']

            new_order.save()

            cart = Cart.objects.all().filter(user=user)
    
            list_of_order_items = []
            for current_cart_item in cart:
                new_order_item = OrderItem()

                new_order_item.menu_item = current_cart_item.menu_item
                new_order_item.quantity = current_cart_item.quantity
                new_order_item.unit_price = current_cart_item.unit_price
                new_order_item.price = current_cart_item.price
                new_order_item.order = Order.objects.get(pk=new_order.id)
                new_order_item.save()
                list_of_order_items.append(model_to_dict(new_order_item))
                new_order.total += new_order_item.price
                current_cart_item.delete()
            
            new_order.save()
            
            context = {
                    "message":"200 - OK.",
                    "data": list_of_order_items
            }
            return Response(context, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if(self.request.method=='GET'):
            return [IsAuthenticated()]
        
        return [IsAuthenticated()]



"""
Order Management Endpoint: 
    - /api/orders/{orderId}

Role:
    - Customer

Purpose: 
    - GET. Returns all items for this order id. 
        If the order ID doesn’t belong to the current user, 
        it displays an appropriate HTTP error status code.
    - PUT. PATCH. Updates the order. A manager can use this endpoint to set a delivery crew to this order, 
        and also update the order status to 0 or 1.
        If a delivery crew is assigned to this order and the status = 0, 
        it means the order is out for delivery.
        If a delivery crew is assigned to this order and the status = 1, 
        it means the order has been delivered.

Role:
    - Manager

Purpose: 
    - DELETE. Deletes this order.

Role:
    - Delivery Crew

Purpose:    
    - GET. Returns all orders with order items assigned to the delivery crew.
    - PATCH. A delivery crew can use this endpoint to update the order status to 0 or 1. 
        The delivery crew will not be able to update anything else in this order.
"""

class SingleOrderView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, id):
        if request.auth == None:
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery crew').exists():
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        token = Token.objects.filter(user=user)
        if token:
            order = get_object_or_404(Order, pk=id)
            if user != order.user:
                return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)    
            else:
                print(" --------------- ")
                context = {
                    "message":"200 - OK.",
                    "data": model_to_dict(order)
                }
                return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, id):
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=id)
            if order:
                payload = self.request.data
                order.delivery_crew = User.objects.get(pk=payload['delivery_crew_id'])
                order_status = payload['status']
                if order_status in [True, False]:
                    order.status = order_status
                else: 
                    return Response({"message":"400 - Unsuccessful."}, status=status.HTTP_400_BAD_REQUEST)                   
                order.save()
                return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"404 - Not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"401 - Forbidden."}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, id):
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=id)
            if order:
                payload = self.request.data
                if 'delivery_crew_id' in payload:
                    order.delivery_crew = User.objects.get(pk=payload['delivery_crew_id'])
                if 'status' in payload and (payload['status'] in [True, False]):
                    order.status = payload['status'] 
                order.save()
                return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"404 - Not found."}, status=status.HTTP_404_NOT_FOUND)    
        elif request.user.groups.filter(name='Delivery crew').exists():
            order = get_object_or_404(Order, pk=id)
            if order:
                payload = self.request.data
                if 'status' in payload:
                    order_status = payload['status']
                    if order_status in [True, False]:
                        order.status = order_status   
                order.save()
                return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"404 - Not found."}, status=status.HTTP_404_NOT_FOUND)
            
        else:
           return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order, pk=id)
            if order:
                order.delete()
                return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"404 - Not found."}, status=status.HTTP_404_NOT_FOUND)    
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        if(self.request.method in ['GET', 'PUT', 'PATCH', 'DELETE']):
            return [IsAuthenticated()]
        return [IsAuthenticated()]


"""
[[User Group Management Endpoints: /api/groups/manager/users]]

Role:
    - Manager

Purpose:
    - GET. Returns all managers
    - POST. Assigns the user in the payload to the manager group and returns 201-Created
    - DELETE. Removes this particular user from the manager group and returns 200 – Success if everything is okay. 
    If the user is not found, returns 404 – Not found


"""
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def managers(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups__name="Manager").values('username', 'email')
        context = {
            "message":"200 - OK.",
            "data": managers
        }
        return Response(context, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        if request.user.groups.filter(name='Manager').exists():
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name="Manager")
                managers.user_set.add(user)

            return Response({"message":"201 - Created."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
    return Response({"message":"400 - Bad Request"}, status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE',])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def manager_view(request, id):
    if request.user.groups.filter(name='Manager').exists():
        user = get_object_or_404(User, pk=id)
        if user:
            managers = Group.objects.get(name="Manager")
            managers.user_set.remove(user)
            return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"404 - Not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)


"""
[[User Group Management Endpoints: /api/groups/delivery-crew/users]]

Role:
    - Manager

Purpose:
    - GET. Returns all delivery crew.
    - POST. Assigns the user in the payload to delivery crew group and returns 201-Created HTTP.
    - DELETE. Removes this user from the delivery crew group and returns 200 – Success if everything is okay. 
    If the user is not found, returns  404 – Not found

"""
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delivery_crew(request):
    if request.method == 'GET':
        delivery_crew_members = User.objects.filter(groups__name="Delivery crew").values('username', 'email')
        context = {
            "message":"200 - OK.",
            "data": delivery_crew_members
        }
        return Response(context, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        if request.user.groups.filter(name='Manager').exists():
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                delivery_crew_members = Group.objects.get(name="Delivery crew")
                delivery_crew_members.user_set.add(user)

                return Response({"message":"201 - Created."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
    return Response({"message":"400 - Bad Request"}, status.HTTP_400_BAD_REQUEST)

        
@api_view(['DELETE',])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delivery_crew_view(request, id):
    if request.user.groups.filter(name='Manager').exists():
        user = get_object_or_404(User, pk=id)
        if user:
            delivery_crew_members = Group.objects.get(name="Delivery crew")
            delivery_crew_members.user_set.remove(user)
            return Response({"message":"200 - Success."}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"404 - Not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"message":"403 - Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
    
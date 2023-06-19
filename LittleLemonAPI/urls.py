from django.urls import path

from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:id>', views.SingleOrderView.as_view()),
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:id>', views.manager_view),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:id>', views.delivery_crew_view),
]
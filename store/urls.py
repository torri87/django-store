from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.get_items, name='items-api'),
    path('', views.items_page, name='items-page'),
]
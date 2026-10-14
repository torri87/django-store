from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Product, Category, User
from .serializers import ProductSerializer, CategorySerializer, RegisterSerializer
from rest_framework.generics import CreateAPIView


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filterset_fields = ['category']
    search_fields = ['name']
    ordering_fields = ['price', 'time_created']


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
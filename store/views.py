from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Product, Category, Order
from .serializers import ProductSerializer, CategorySerializer, RegisterSerializer, ProfileSerializer, OrderSerializer
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from .pagination import ProductPagination
from django.http import JsonResponse
from .permissions import IsAdminReadOnly


def health_check(request):
    return JsonResponse({'status': 'ok'})


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAdminReadOnly]
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filterset_fields = ['category']
    search_fields = ['name']
    ordering_fields = ['price', 'time_created']


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAdminReadOnly]
    serializer_class = CategorySerializer


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class OrderViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')
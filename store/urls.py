from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, RegisterView, ProfileView, OrderViewSet, health_check
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()

router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', ProfileView.as_view(), name='me'),
]
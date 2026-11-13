from django.db import transaction
from rest_framework import serializers
from .models import Product, Category, User, OrderItem, Order, Favorite
from django.contrib.auth.password_validation import validate_password as check_password
from django.core.exceptions import ValidationError


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'description', 'price', 'stock', 'time_created']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_password(self, value):
        try:
            check_password(value)
        except ValidationError as error:
            raise serializers.ValidationError(list(error.messages))

        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone']
        extra_kwargs = {'username': {'read_only': True}, 'id': {'read_only': True}}


class OrderItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        extra_kwargs = {'price': {'read_only': True}}

    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Цей товар не доступний для покупки.')
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, allow_empty=False)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'status', 'time_created', 'items', 'total']
        read_only_fields = ['id', 'status', 'time_created']

    def get_total(self, obj):
        total = 0
        for item in obj.items.all():
            total += item.price * item.quantity

        return total

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        with transaction.atomic():
            order = Order.objects.create(user=user)

            for item in items_data:
                product = Product.objects.select_for_update().get(id=item['product'].id)
                quantity = item['quantity']

                if product.stock < quantity:
                    raise serializers.ValidationError(f"В наявності недостатньо {product.name}: на складі {product.stock}")

                product.stock -= quantity
                product.save()

                OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)

        return order

    def validate_items(self, value):
        ids = []
        for item in value:
            ids.append(item['product'].id)

        unique_ids = set(ids)

        if len(ids) != len(unique_ids):
            raise serializers.ValidationError("Один і той ж товар вказано декілька разів.")

        return value


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'product', 'time_created']
        read_only_fields = ['id', 'time_created']

    def validate_product(self, value):
        user = self.context['request'].user
        already_favorite = Favorite.objects.filter(user=user, product=value).exists()
        if already_favorite:
            raise serializers.ValidationError("Цей Товар уже є в обраному.")
        return value
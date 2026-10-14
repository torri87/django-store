from rest_framework import serializers
from .models import Product, Category, User
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
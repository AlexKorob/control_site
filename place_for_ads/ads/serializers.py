import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Image, Ad, Category
from .utils import AdSerializerMixin
from rest_framework.authtoken.models import Token
from rest_framework_recursive.fields import RecursiveField
from rest_framework.parsers import ParseError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_active', 'is_staff')


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'phone')

    def validate_phone(self, value):
        reg = r'^\+?1?\d{9,15}$'
        if re.match(reg, value):
            return value
        raise serializers.ValidationError("Please enter correct number +xxxxxxxxxx")

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError("Password must contain grade then 7 symbols")
        if password.islower():
            raise serializers.ValidationError("Password must contain minimum one Upper letter")
        if password.isupper():
            raise serializers.ValidationError("Password must contain minimum one lower letter")
        if password.isdigit():
            raise serializers.ValidationError("Password must contains minimum one lower and upper letter")
        return password


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', )


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.ReadOnlyField(source="parent.name")

    class Meta:
        model = Category
        fields = ('name', 'parent')


class AdSerializer(AdSerializerMixin, serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    images = ImageSerializer(many=True, read_only=True)
    category_branch = serializers.CharField(source="category.get_full_path", read_only=True)
    category = serializers.CharField()

    class Meta:
        model = Ad
        fields = ('id', 'creator', 'title', 'status', 'category', 'category_branch', 'images',
                  'description', 'price', 'contractual')

    def create(self, data):
        return self.mix(data, self.context, "create")

    def update(self, instance, data):
        data = self.mix(data, self.context, "update", instance)
        return super().update(instance, data)

    def partial_update(self, instance, data):
        data =  self.mix(data, self.context, "update", instance)
        return super().update(instance, data)

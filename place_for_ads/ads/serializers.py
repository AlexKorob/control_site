import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Image, Ad, Category, Favorite
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


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.ReadOnlyField(source="parent.name")

    class Meta:
        model = Category
        fields = ('name', 'parent')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image', 'ad')

    def validate_ad(self, ad):
        user = self.context["request"].user.id
        if user != ad.creator.id:
            raise serializers.ValidationError("This is not your ad")
        return ad


class ImageAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image", )


class AdSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    images = ImageAdSerializer(many=True, required=False, read_only=True)
    category_branch = serializers.CharField(source="category.get_full_path", read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all(), required=True)

    class Meta:
        model = Ad
        fields = ('id', 'creator', 'title', 'status', 'category', 'category_branch', 'images',
                  'description', 'price', 'contractual')


class FavoriteShowSerializer(serializers.ModelSerializer):
    ad = AdSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'ad', 'user')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('ad', )

    def create(self, data):
        data["user"] = User.objects.get(id=self.context["request"].user.id)
        return Favorite.objects.create(**data)

    def validate_ad(self, data):
        user = self.context["request"].user.id

        if Favorite.objects.filter(user=user, ad=data).exists():
            raise serializers.ValidationError("This ad was added to favorites")
        return data

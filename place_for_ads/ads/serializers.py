import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User


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

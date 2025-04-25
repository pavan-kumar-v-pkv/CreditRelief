from rest_framework import serializers
from .models import User

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['aadhar_id', 'name', 'email', 'annual_income']
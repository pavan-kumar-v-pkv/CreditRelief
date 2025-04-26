from rest_framework import serializers
from .models import User, Loan
from rest_framework import serializers

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['aadhar_id', 'name', 'email', 'annual_income']

class LoanApplySerializer(serializers.Serializer):
    unique_user_id = serializers.UUIDField()
    loan_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    term_period = serializers.IntegerField()
    disbursement_date = serializers.DateField()
    loan_type = serializers.CharField(default="credit_card") # fixed value

class MakePaymentSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
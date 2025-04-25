from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterUserSerializer, LoanApplySerializer
from .models import User, Loan, CreditScore
from .tasks import calculate_credit_score_task
from datetime import timedelta
from uuid import UUID
from decimal import Decimal

class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            calculate_credit_score_task.delay(str(user.id))
            return Response({
                'unique_user_id': user.id,
                'error': None
            }, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ApplyLoanView(APIView):
    def post(self, request):
        serializer = LoanApplySerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user = User.objects.get(id=data['unique_user_id'])
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=400)

            # Eligibility rules
            try:
                score = CreditScore.objects.get(user=user).score
            except CreditScore.DoesNotExist:
                return Response({'error': 'Credit score not found'}, status=400)

            if score < 450:
                return Response({'error': 'Credit score too low for loan'}, status=400)

            if user.annual_income < 150000:
                return Response({'error': 'Annual income too low'}, status=400)

            if data['loan_amount'] > 5000:
                return Response({'error': 'Loan amount exceeds 5000 limit'}, status=400)

            # EMI Rule: must not exceed 20% of monthly income
            monthly_income = user.annual_income / 12
            interest_per_month = Decimal(data['interest_rate']) / Decimal(100)
            total_interest = (data['loan_amount']) * interest_per_month * data['term_period']
            total_payable = (data['loan_amount']) + total_interest
            base_emi = total_payable / data['term_period']

            if base_emi > Decimal('0.2') * Decimal(monthly_income):
                return Response({'error': 'EMI exceeds 20% of monthly income'}, status=400)

            if total_interest < 50:
                return Response({'error': 'Total interest must exceed Rs. 50'}, status=400)

            # Save Loan
            loan = Loan.objects.create(
                user=user,
                loan_amount=data['loan_amount'],
                interest_rate=data['interest_rate'],
                term_period=data['term_period'],
                disbursement_date=data['disbursement_date']
            )

            # Generate EMI schedule
            emi_schedule = []
            for i in range(data['term_period']):
                emi_date = data['disbursement_date'] + timedelta(days=30 * (i+1))
                emi_schedule.append({
                    "date":emi_date,
                    "amount_due": round(base_emi, 2) if i < data['term_period'] - 1 else round(total_payable - base_emi * (data['term_period'] - 1), 2)
                })
            return Response({
                "loan_id": loan.id,
                "due_dates": emi_schedule,
                "error": None
            })
        return Response({"error": serializer.errors}, status=400)
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterUserSerializer, LoanApplySerializer, MakePaymentSerializer, GetStatementSerializer
from .models import User, Loan, CreditScore, Billing, DuePayment
from .tasks import calculate_credit_score_task
from datetime import timedelta, date
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


class MakePaymentsView(APIView):
    def post(self, request):
        serializer = MakePaymentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            loan_id = data['loan_id']
            amount = data['amount']

            # Find all billing entries for the loan
            billings = Billing.objects.filter(loan__id=loan_id).order_by('billing_date')

            if not billings.exists():
                return Response({'error': 'No billing found for this loan'}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate over billings to find unpaid billing
            for billing in billings:
                due_payment, created = DuePayment.objects.get_or_create(billing=billing)

                if due_payment.status == 'pending':
                    # Add the payment to existing paid_amount
                    due_payment.paid_amount += amount

                    if due_payment.paid_amount >= billing.min_due:
                        due_payment.paid_amount = billing.min_due  # Do not exceed min_due
                        due_payment.status = 'paid'
                        due_payment.payment_date = date.today()

                    due_payment.save()
                    remaining_due = billing.min_due - due_payment.paid_amount
                    remaining_due = max(Decimal('0.00'), remaining_due)  # to avoid negative

                    return Response({
                        "billing_id": billing.id,
                        "amount_paid": str(due_payment.paid_amount),
                        "remaining_due": str(remaining_due),
                        "status": due_payment.status,
                        "error": None
                    }, status=status.HTTP_200_OK)

            return Response({'error': 'All dues are already paid for this loan'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetStatementView(APIView):
    def post(self, request):
        serializer = GetStatementSerializer(data=request.data)
        if serializer.is_valid():
            loan_id = serializer.validated_data['loan_id']
            try:
                loan = Loan.objects.get(id=loan_id)
            except Loan.DoesNotExist:
                return Response({'error': 'Loan not found'}, status=status.HTTP_400_BAD_REQUEST)

            billings = Billing.objects.filter(loan=loan).order_by('billing_date')

            past_transactions = []
            upcoming_transactions = []

            for billing in billings:
                due_payment = DuePayment.objects.filter(billing=billing).first()

                if due_payment and due_payment.status == 'paid':
                    past_transactions.append({
                        "date": billing.billing_date,
                        "principal": billing.principal_balance,
                        "interest": billing.interest_accrued,
                        "amount_paid": due_payment.paid_amount
                    })
                else:
                    upcoming_transactions.append({
                        "date": billing.billing_date,
                        "amount_due": billing.min_due
                    })

            return Response({
                "past_transactions": past_transactions,
                "upcoming_transactions": upcoming_transactions,
                "error": None
            }, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
from celery import shared_task
from .models import CreditScore, User, Loan, Billing
import pandas as pd
from decimal import Decimal
from django.utils import timezone
from datetime import date, timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@shared_task
def calculate_credit_score_task(user_id):
    try:
        user = User.objects.get(id=user_id)
        aadhar_id = user.aadhar_id

        # Load the CSV file
        csv_path = os.path.join(BASE_DIR, 'transactions.csv')
        df = pd.read_csv(csv_path)
        df = df[df['user'] == aadhar_id]

        balance = 0
        for _, row in df.iterrows():
            amount = float(row['amount'])
            if row['transaction_type'] == 'CREDIT':
                balance += amount
            else:
                balance -= amount

        if balance >= 1000000:
            score = 900
        elif balance <= 10000:
            score = 300
        else:
            score = 300 + int((balance - 10000) / 15000) * 10
            score = min(score, 900)

        # No need to fetch user again
        CreditScore.objects.update_or_create(user=user, defaults={'score': score, 'calculated_at': timezone.now()})
    except Exception as e:
        print(f"Error calculating score for user {user_id}: {e}")


@shared_task
def generate_billing_for_today():
    today = date.today()
    loans = Loan.objects.all()

    for loan in loans:
        loan_age_days = (today - loan.disbursement_date).days
        if loan_age_days > 0 and loan_age_days % 30 == 0:
            total_interest = loan.loan_amount * (loan.interest_rate / Decimal('100')) * loan.term_period
            total_payable = loan.loan_amount + total_interest
            emi = total_payable / loan.term_period

            Billing.objects.create(
                loan=loan,
                billing_date=today,
                due_date=today + timedelta(days=15),
                principal_balance=loan.loan_amount,
                interest_accrued=round(total_interest / loan.term_period, 2),
                min_due=round(emi, 2)
            )

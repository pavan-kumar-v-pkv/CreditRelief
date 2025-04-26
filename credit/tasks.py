from celery import shared_task
from .models import CreditScore, User
import pandas as pd
from decimal import Decimal
from django.utils import timezone
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@shared_task
def calculate_credit_score_task(aadhar_id, user_id):
    try:
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

        user = User.objects.get(id=user_id)
        CreditScore.objects.update_or_create(user=user, defaults={'score': score, 'calculated_at': timezone.now()})
    except Exception as e:
        print(f"Error calculating score for user {user_id}: {e}")

from .models import Loan, Billing
from decimal import Decimal
from datetime import date, timedelta

def generate_billing_for_today():
    today = date.today()
    loans = Loan.objects.all()

    for loan in loans:
        # Check if this loan needs billing
        loan_age_days = (today - loan.disbursement_date).days
        if loan_age_days > 0 and loan_age_days % 30 == 0:
            principal_balance = loan.loan_amount
            daily_interest_rate = loan.interest_rate / Decimal('365')
            total_interest = principal_balance * daily_interest_rate * Decimal('30')
            min_due = (principal_balance * Decimal('0.03')) + total_interest

            Billing.objects.create(
                loan=loan,
                billing_date=today,
                due_date=today + timedelta(days=15),
                principal_balance=principal_balance,
                interest_accrued=round(total_interest, 2),
                min_due=round(min_due, 2)
            )
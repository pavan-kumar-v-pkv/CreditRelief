from .models import Loan, Billing
from decimal import Decimal
from datetime import date, timedelta

def generate_billing_for_today():
    today = date.today()
    loans = Loan.objects.all()

    for loan in loans:
        loan_age_days = (today - loan.disbursement_date).days
        if loan_age_days > 0 and loan_age_days % 30 == 0:
            # Calculate total interest over full term
            total_interest = loan.loan_amount * (loan.interest_rate / Decimal('100')) * loan.term_period
            # Total amount to repay (Principal + Interest)
            total_payable = loan.loan_amount + total_interest
            # EMI = total payable / number of months
            emi = total_payable / loan.term_period

            # Create Billing
            Billing.objects.create(
                loan=loan,
                billing_date=today,
                due_date=today + timedelta(days=15),  # 15 days grace period for payment
                principal_balance=loan.loan_amount,  # Optional, just for record
                interest_accrued=round(total_interest / loan.term_period, 2),  # per month interest
                min_due=round(emi, 2)  # EMI amount
            )

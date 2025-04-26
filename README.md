# CreditRelief

**Backend Django Application** for Credit Service Management.

---

## Project Overview

CreditRelief helps simulate:

* User loan registrations
* Credit score calculation based on account transactions
* Loan application and EMI breakup
* Monthly billing and interest calculation
* EMI repayments and dues tracking
* Full loan statement generation

This backend uses:

* **Django REST Framework**
* **Celery + Redis** for async credit score calculation
* **Custom cron job** for billing generation

---

## How to Run the Project Locally

1. Clone the repository (private)
2. Create and activate a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Set up Redis server (for Celery):
```bash
brew install redis
brew services start redis
```
5. Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```
6. Start Django server:
```bash
python manage.py runserver
```
7. Start Celery worker:
```bash
celery -A creditrelief worker --loglevel=info
```

---

## APIs Implemented

| Endpoint                    | Description                                                       |
|-----------------------------|-------------------------------------------------------------------|
| `POST /api/register-user/`  | Register a new user, trigger async credit score calculation       |
| `POST /api/apply-loan/`     | Apply for a loan against credit card after eligibility validation |
| `POST /api/make-payment/`   | Make EMI payments, update dues                                    |
| `POST /api/get-statement/`  | Fetch past and upcoming loan transactions                         |

---

## Important Details

* Credit Score calculated from transactions data (CSV)
* Billing generated every 30 days
* Daily interest accrued, minimum due calculated
* Payment validations:
  * No duplicate payments
  * Past dues must be cleared before future billing
* Statement shows both paid EMIs and future dues

---

## Author

**Pavan Kumar V**

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
* **Django-Celery-Beat** for automatic daily cron job scheduling

---

## How to Run the Project Locally

1. Clone the repository (private)
2. Create and activate a virtual environment
```bash
python3 -m venv env
source env/bin/activate # Linux/Mac
env\Scripts\activate     # Windows
```
3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Set up Redis server (for Celery):

- **macOS users**:
  ```bash
  brew install redis
  brew services start redis
  ```

- **Windows users**:
  - Download Redis installer from: https://github.com/microsoftarchive/redis/releases
  - Install Redis as a Windows Service.
   
- **Linux users**:
  ```bash
  sudo apt update
  sudo api install redis-server
  sudo systemctl start redis
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
8. Start Celery Beat (for cron jobs):
```bash
celery -A creditrelief beat --loglevel=info
```
9. Test APIs using Postman / curl commands.
10. (Optional) Run billing manually for testing purposes):
```bash
python manage.py generate_bills
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

## Important Details (for clarification) 

* **Billing Generation**:
  * Bills are generated every 30 days after loan disbursement.
  * Cron job (Celery Beat) automatically triggers billing daily.
  * Manual billing can also be triggered using `python manage.py generate_bills`.
* **Billing Amount**:
  * Due amount (min_due) = EMI shown at loan application.
  * No extra hidden charges or recalculations.
* **Interest Calculation**:
  * Interest Rate is treated monthly as per assignment.
  * 12% → 0.12 directly (divide by 100 once).
* Partial Payments:
  * Partial payments are accepted.
  * Remaining due is shown properly in `/api/make-payment/` and `/api/get-statement/`.
* **Statement Behavior**:
  * If full EMI is not paid, upcoming_transactions show the pending amount.
  * Once full EMI is cleared, the billing entry moves to past_transactions.
  * Clear segregation between pending and paid bills.
* **Credit Score Calculation**:
  * Based on provided `transactions.csv` file.
  * If aadhar_id matches, credit score is calculated.
  * If no matching transaction found, default score is 300.
  * Minimum credit score needed to apply for a loan: 450.

### Important Testing Behavior (Clarification)

* After partial payment, `/api/get-statement/` shows the remaining amount dynamically.
* Until full EMI is paid, it stays in `upcoming_transactions`.
* Only after full EMI is paid, it moves to `past_transactions`.
* Bills for next month will appear only after 30 more days (next billing cycle).

---

## Author

**Pavan Kumar V**

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

- **macOS users**:
  ```bash
  brew install redis
  brew services start redis
  ```

- **Windows users**:
  - Download Redis installer from: https://github.com/microsoftarchive/redis/releases
  - Install Redis as a Windows Service.
  - Start Redis server manually ot through services.msc.
   
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
8. Test APIs using Postman / curl commands.
9. Run billing manually (for test purposes):
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

* Bills are generated every 30 days after loan disbursement.
* When billing is generated:
  * Due amount (min_due) is exactly equal to the EMI shown during loan application.
* This ensures:
  * `/api/apply-loan/` EMI and billing amounts match exactly.
* At the time of testing, only 1 EMI will be visible in the system.
  * Subsequent EMIs will appear only after 60 days, 90 days, etc., according to 30-day billing cycle. (Have to run `python manage.py generate_bills` manually again)
  * This can be updated.
* Interest Rate is treated directly as monthly as per assignment expectations. (12% → 0.12 after dividing by 100)
* Partial Payments:
  * Allowed.
  * Remaining due amount shown in API response.
* Transactions CSV:
  * Aadhar ID provided during registration should match an entry in the `transactions.csv` file.
  * Otherwise, default credit score = 300 (loan rejected if score < 450).

* When a user makes a partial payment for a billing cycle,
the entire billing amount (min_due) will continue to appear under upcoming_transactions in /api/get-statement/.
* Partial payments are recorded internally but the due amount displayed remains the full EMI amount until it is fully paid.
* Only after full payment of the billing’s min_due, the billing entry moves to past_transactions.
* This ensures billing and due tracking is clean, simple, and avoids confusion with partial EMIs.
* This behavior is designed based on Bright Money assignment PDF: "All due amounts must be repaid within the specified tenure."


---

## Author

**Pavan Kumar V**

# CreditRelief 💳

> Django REST API for credit lifecycle management — loan registration, EMI scheduling, async credit scoring, and statement generation.

CreditRelief is a backend service that simulates a real-world credit management system: users register loans, the system calculates credit scores asynchronously via Celery, schedules EMI billing via cron, and generates monthly statements.

## Features

- **Loan lifecycle** — registration, approval, EMI schedule generation, repayment tracking
- **Async credit scoring** — Celery worker processes credit score calculations off the request thread
- **Automated billing** — Celery Beat cron job runs daily EMI billing
- **REST API** — full DRF API for all loan and account operations
- **Statement generation** — full loan statement with interest breakdown per period

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4 + Django REST Framework |
| Async tasks | Celery + Redis |
| Scheduler | Django-Celery-Beat |
| Database | SQLite (dev) / PostgreSQL (prod-ready) |
| Auth | Django session + DRF token auth |

## Architecture

```
creditrelief/
├── credit/
│   ├── models.py          # Loan, Account, Transaction, EMISchedule models
│   ├── views.py           # DRF ViewSets
│   ├── serializers.py     # Input/output serializers
│   ├── tasks.py           # Celery tasks (credit score, billing)
│   └── urls.py
├── creditrelief/
│   ├── settings.py
│   └── celery.py          # Celery app config
└── manage.py
```

## Setup

```bash
git clone https://github.com/pavan-kumar-v-pkv/CreditRelief
cd CreditRelief
python -m venv env && source env/bin/activate
pip install -r requirements.txt

# Start Redis (required for Celery)
brew install redis && brew services start redis  # macOS
# or: sudo apt install redis-server && sudo systemctl start redis

python manage.py migrate
python manage.py runserver

# In separate terminals:
celery -A creditrelief worker --loglevel=info
celery -A creditrelief beat --loglevel=info
```

## Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/loans/register/` | Register a new loan |
| GET | `/api/loans/{id}/schedule/` | Get EMI schedule |
| POST | `/api/loans/{id}/repay/` | Record a repayment |
| GET | `/api/accounts/{id}/statement/` | Get full loan statement |
| GET | `/api/accounts/{id}/credit-score/` | Get current credit score |

## How Async Scoring Works

1. User registers a loan → API returns immediately
2. A Celery task is queued to calculate credit score based on transaction history
3. Score is persisted to the DB asynchronously
4. Celery Beat triggers daily billing job at midnight to calculate dues and update EMI status

## License

MIT

# 🎟️ Event Booking Platform with Django & Stripe

A professional-grade Event Booking API built with **Django REST Framework**, **JWT authentication**, **Stripe** for payments, **Celery** with **Redis** for async tasks (like password reset emails), and full user authentication flow including one-time secure password reset.

---

## 🔧 Features

* ✅ User Registration & JWT Login (Attendee / Organizer roles)
* ✅ Secure Password Reset with Celery + Gmail (one-time token)
* ✅ Event Creation & Management (by organizers)
* ✅ Ticket Booking system with real-time ticket availability
* ✅ Stripe Payment Gateway integration (test mode)
* ✅ Post-payment ticket confirmation & receipt handling
* ✅ Platform fee logic with revenue tracking
* ✅ Developer-friendly REST APIs with proper response formatting
* ✅ Swagger/OpenAPI ready for testing APIs
* ✅ Environment-based config with `.env`

---

## 📁 Tech Stack

| Layer         | Tech                                |
| ------------- | ----------------------------------- |
| Backend       | Django, Django REST Framework       |
| Auth          | JWT via `SimpleJWT`                 |
| Payments      | Stripe                              |
| Async Tasks   | Celery + Redis                      |
| Database      | PostgreSQL (or SQLite in dev)       |
| Email Service | Gmail SMTP (via Django `send_mail`) |
| Frontend      | API-first (use Postman/Swagger)     |

---

## 📂 Project Structure

```
event_booking/
├── bookings/              # Booking logic, history, availability
├── events/                # Event models, views
├── payments/              # Stripe integration + receipts
├── users/                 # Custom user model & auth
│   └── templates/users/   # HTML for password reset page
├── event_booking/         # Main project config (settings.py, celery.py)
├── .env                   # Environment variables
├── requirements.txt
├── README.md
└── manage.py
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Vivek11sharma/event_booking.git
cd event-booking
```

### 2. Create & Activate Virtual Environment

```bash
# On Mac:
python -m venv env
source env/bin/activate

# On Windows use:
env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root:

```env
# Stripe
STRIPE_SECRET_KEY=your_test_secret_key
STRIPE_PUBLISHABLE_KEY=your_test_publishable_key
STRIPE_WEBHOOK_SECRET=your_test_STRIPE_WEBHOOK_SECRET_key
PLATFORM_FEE_PERCENTAGE=10

```


### 5. Set Up PostgreSQL Database

Make sure PostgreSQL is installed and running. Then:

1. Access PostgreSQL as a superuser (e.g., `postgres`):

```bash
psql -U postgres
```

2. Create the database and user:

```sql
CREATE DATABASE event_booking;
CREATE USER vivek WITH PASSWORD 'vivek123';
GRANT ALL PRIVILEGES ON DATABASE event_booking1 TO vivek;
```

3. Switch to the database and assign schema privileges:

```sql
\c event_booking
GRANT ALL PRIVILEGES ON SCHEMA public TO vivek;
ALTER SCHEMA public OWNER TO vivek;
```

4. Exit psql:

```sql
\q
```

Make sure your `settings.py` contains the following in the `DATABASES` section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'event_booking',
        'USER': 'vivek',
        'PASSWORD': 'vivek123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

### 6. Apply Migrations & Create Superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit: [http://localhost:8000/admin](http://localhost:8000/admin)

---

### 8. Run Redis Server (for async tasks like email)

Make sure Redis is installed before running:

```bash
redis-server
```

---

### 9. Run Celery Worker

```bash
celery -A event_booking worker --loglevel=info
```

---

Let me know if you'd like me to regenerate the entire README with these changes applied so you can copy-paste it all at once.


Visit: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 🔐 API Endpoints Summary

### 🏢 User APIs

| Endpoint                                          | Method | Description              |
| ------------------------------------------------- | ------ | ------------------------ |
| `/api/users/register/`                            | POST   | Register user            |
| `/api/users/login/`                               | POST   | JWT login                |
| `/api/users/token/refresh/`                       | POST   | Refresh token            |
| `/api/users/password-reset/request/`              | POST   | Request password reset   |
| `/api/users/password-reset/confirm/<uuid:token>/` | POST   | Set new password         |
| `/reset-password/<uuid:token>/`                   | GET    | Password reset HTML page |

### 🎟️ Event APIs (Organizer Only)

| Endpoint              | Method | Description               |
| --------------------- | ------ | ------------------------- |
| `/api/create-event/`  | POST   | Create event with tickets |
| `/api/my-events/`     | GET    | Get all my events         |
| `/api/events/<id>/`   | PATCH  | Update event              |
| `/api/events/<id>/`   | DELETE | Delete event              |
| `/api/search-events/` | GET    | Public event search       |

### 💼 Booking APIs

| Endpoint                            | Method | Description                  |
| ----------------------------------- | ------ | ---------------------------- |
| `/api/bookings/create/`             | POST   | Create booking               |
| `/api/bookings/my-bookings/`        | GET    | Get my bookings              |
| `/api/bookings/my-receipts/`        | GET    | View receipts (Stripe links) |
| `/api/bookings/organizers/revenue/` | GET    | Organizer revenue summary    |

---

## ✅ Testing Stripe Payments

Use test card:

```
Card Number: 4242 4242 4242 4242
Expiry: Any future date
CVV: Any 3-digit
ZIP: Any
```

Check receipt in `my-receipts` endpoint.

---

## 📜 License

MIT License

---

## 🤝 Credits

Built with ❤️ by **Vivek Sharma**
Python | Django | Celery | Stripe | PostgreSQL | Redis

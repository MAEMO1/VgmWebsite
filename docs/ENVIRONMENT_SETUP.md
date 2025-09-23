# Environment Setup

## Backend Environment Variables

Create `backend/.env` with the following variables:

```env
# Database Configuration
DATABASE_URL=postgres://postgres:postgres@localhost:5432/vgm

# Security
SESSION_SECRET=change-me-to-a-secure-random-string
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:3000

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=smtp.example.org
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=secret
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@vgm.example.org

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PLATFORM_FEE_PERCENT=5

# External API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
MAPS_BACKEND_API_KEY=

# Application Settings
FLASK_ENV=development
FLASK_APP=main.py
PORT=5000

# Monitoring (Optional)
SENTRY_DSN=
```

## Frontend Environment Variables

Create `frontend/.env.local` with the following variables:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Internationalization
NEXT_PUBLIC_DEFAULT_LOCALE=nl
NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps

# External API Keys
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Monitoring (Optional)
NEXT_PUBLIC_SENTRY_DSN=
```

## Required Services

1. **PostgreSQL 16**: Database for the application
2. **Redis 7**: Caching and session storage
3. **Google Maps API**: For map functionality (get API key from Google Cloud Console)
4. **Stripe Account**: For payment processing (test keys for development)

## Setup Commands

```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit the files with your actual values
# Then run migrations
python backend/manage.py migrate
python backend/manage.py createsuperuser
```

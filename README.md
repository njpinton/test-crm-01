# CRM System

A B2B sales CRM system built with Django, HTMX, Alpine.js, and Tailwind CSS, designed for deployment on Google Cloud Platform.

## Features

- **User Account Management**: Staff authentication with check-in/check-out tracking
- **Pipeline Management**: 9-stage deal tracking (Screening → Estimating → Nurture → Negotiation → Project Turnover)
- **Client Dashboard**: Comprehensive client interaction tracking (calls, emails, site visits)
- **File Management**: Estimate uploads and document storage
- **Email Integration**: Gmail and Outlook OAuth2 support with email templates
- **Activity Logging**: Complete audit trail of all client interactions
- **Invoicing & Payments**: Invoice tracking and payment integration
- **Analytics**: Deal funnel visualization and staff performance metrics

## Tech Stack

- **Backend**: Django 5.0 (Python 3.12+)
- **Frontend**: HTMX + Alpine.js + Tailwind CSS
- **Database**: PostgreSQL 15+ (Cloud SQL)
- **Storage**: Google Cloud Storage
- **Deployment**: Cloud Run (GCP)
- **Task Queue**: Cloud Tasks

## Prerequisites

- Python 3.12 or higher
- UV package manager
- Google Cloud SDK (for deployment)
- PostgreSQL (for production-like local development)

## Local Development Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd crm
```

### 2. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create virtual environment and install dependencies

```bash
uv venv
uv pip install -r requirements/development.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and configure your settings. For local development, the defaults should work.

### 5. Run migrations

```bash
.venv/bin/python manage.py migrate --settings=config.settings.development
```

### 6. Create a superuser

```bash
.venv/bin/python manage.py createsuperuser --settings=config.settings.development
```

### 7. Run the development server

```bash
.venv/bin/python manage.py runserver --settings=config.settings.development
```

The application will be available at http://localhost:8000

### 8. Access Django Admin

Navigate to http://localhost:8000/admin and log in with your superuser credentials.

## Project Structure

```
crm/
├── apps/
│   ├── accounts/          # User authentication & time tracking
│   ├── clients/           # Client management
│   ├── pipeline/          # Deal pipeline management
│   ├── communications/    # Email, calls, activity logging
│   ├── invoicing/         # Invoice management
│   ├── scheduling/        # Site visit scheduling
│   └── analytics/         # Reporting and dashboards
├── config/
│   ├── settings/
│   │   ├── base.py       # Common settings
│   │   ├── development.py # Local development
│   │   └── production.py  # GCP Cloud Run
│   ├── urls.py
│   └── wsgi.py
├── templates/             # HTML templates
├── static/               # Static assets
├── requirements/         # Python dependencies
├── Dockerfile            # Container configuration
└── manage.py
```

## Testing

Run tests with pytest:

```bash
.venv/bin/pytest
```

Run tests with coverage:

```bash
.venv/bin/pytest --cov=apps --cov-report=html
```

## Code Quality

Format code with Black:

```bash
.venv/bin/black .
```

Sort imports with isort:

```bash
.venv/bin/isort .
```

Lint with flake8:

```bash
.venv/bin/flake8
```

## Deployment to GCP Cloud Run

### Prerequisites

1. Create a GCP project
2. Enable required APIs:
   - Cloud Run
   - Cloud SQL
   - Cloud Storage
   - Secret Manager
   - Cloud Build

3. Create Cloud SQL PostgreSQL instance
4. Create Cloud Storage buckets
5. Set up Secret Manager secrets

### Deploy

```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/crm

# Deploy to Cloud Run
gcloud run deploy crm-app \
    --image gcr.io/PROJECT_ID/crm \
    --platform managed \
    --region us-central1 \
    --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production"
```

See the [deployment guide](/docs/deployment.md) for detailed instructions.

## Environment Variables

See `.env.example` for all available configuration options.

### Required for Production

- `DJANGO_SECRET_KEY`: Django secret key
- `DATABASE_NAME`: PostgreSQL database name
- `DATABASE_USER`: Database user
- `DATABASE_PASSWORD`: Database password
- `CLOUD_SQL_CONNECTION_NAME`: Cloud SQL connection string
- `GS_BUCKET_NAME`: Cloud Storage bucket name
- `GMAIL_CLIENT_ID`: Gmail API client ID
- `GMAIL_CLIENT_SECRET`: Gmail API client secret

## Key Features Documentation

### User Roles

- **Administrator**: Full system access, analytics, user management
- **Business Development Staff**: Pipeline management, client communication
- **Estimator**: File uploads, quote preparation

### Pipeline Stages

1. New Request
2. Engaged
3. Estimate in Progress
4. Estimate Sent
5. Follow-up
6. Negotiation
7. Closed Won
8. Closed Lost (with sub-reason)
9. Declined to Bid (with sub-reason)

### Check-in/Check-out System

Staff can track their work hours through the check-in/check-out widget in the navigation bar. Time logs are stored and can be viewed in the Django Admin.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and code quality checks
4. Submit a pull request

## License

Proprietary - All Rights Reserved

## Support

For issues or questions, contact the development team or create an issue in the repository.

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Project setup
- ✅ User authentication
- ✅ Check-in/check-out tracking
- ✅ Django Admin configuration

### Phase 2: Pipeline (Upcoming)
- Deal management
- File uploads
- Pipeline board view

### Phase 3: Client Dashboard
- Communication tools
- Email integration
- Activity logging

### Phase 4: Background Tasks
- Async email sending
- Calendar integration
- Payment processing

### Phase 5: Analytics
- Reporting dashboards
- Data export
- Performance metrics

### Phase 6: AI/Automation (Future)
- Lead scoring
- Email sentiment analysis
- Automated follow-ups

# 🐳 Docker Setup Guide

## Prerequisites

- **Docker Desktop** installed and running
  - Download from: https://www.docker.com/products/docker-desktop
  - Ensure Docker daemon is running

## Quick Start

### 1. Build and Run

```bash
# Build the image and start services
docker compose up --build

# For background mode:
docker compose up --build -d

# Stop services:
docker compose down
```

### 2. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

### 3. Initial Setup

Run migrations inside the container:

```bash
# Get a shell in the web container
docker compose exec web bash

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Exit container
exit
```

## Environment Configuration

The `.env` file contains environment variables for the app:

```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web
SECRET_KEY=your-secret-key
```

## Useful Docker Commands

```bash
# View logs
docker compose logs -f web

# Run Django commands
docker compose exec web python manage.py <command>

# Rebuild without cache
docker compose build --no-cache

# Remove volumes (deletes data)
docker compose down -v

# SSH into container
docker compose exec web bash
```

## File Structure

```
.
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-container orchestration
├── .dockerignore          # Files to ignore in Docker
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
├── config/
│   └── settings.py       # Django settings (uses decouple)
├── staticfiles/          # Collected static files
├── media/                # User uploaded files
└── ...
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead of 8000
```

### Database Not Resetting
```bash
# Remove volumes and rebuild
docker compose down -v
docker compose up --build
```

### Static Files Not Loading
```bash
docker compose exec web python manage.py collectstatic --noinput
```

### Permission Issues
```bash
# Run with appropriate permissions
docker compose exec -u root web bash
```

## Production Deployment Notes

Before deploying to production:

1. **Set a strong SECRET_KEY** in `.env`
2. **Set DEBUG=False** in `.env`
3. **Update ALLOWED_HOSTS** with your domain
4. **Use PostgreSQL** instead of SQLite (update settings.py)
5. **Use Gunicorn** with a reverse proxy (Nginx)
6. **Enable HTTPS/SSL**
7. **Set up proper logging**
8. **Use Docker secrets** for sensitive data

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/deployment/checklist/)

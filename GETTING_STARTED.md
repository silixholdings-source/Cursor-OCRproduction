# Getting Started with AI ERP SaaS

This guide will help you set up and run the AI ERP SaaS application on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) (latest version)
- [Docker Compose](https://docs.docker.com/compose/install/) (latest version)
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://python.org/) (v3.11 or higher)
- [Git](https://git-scm.com/) (latest version)

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the setup script to automatically configure everything:

```bash
python setup.py
```

This script will:
- Check prerequisites
- Install all dependencies
- Build Docker containers
- Start the development environment
- Show you the application URLs

### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-erp-saas-app
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

3. **Install dependencies**
   ```bash
   # Install root dependencies
   npm install
   
   # Install backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   
   # Install web dependencies
   cd web
   npm install
   cd ..
   
   # Install mobile dependencies
   cd mobile
   npm install
   cd ..
   ```

4. **Start with Docker Compose**
   ```bash
   # For development
   docker-compose -f docker-compose.dev.yml up -d
   
   # For production
   docker-compose up -d
   ```

## Application URLs

Once running, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Web Frontend**: http://localhost:3000
- **PostgreSQL Database**: localhost:5432
- **Redis Cache**: localhost:6379

## Development Commands

### Backend Development
```bash
# Run backend in development mode
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest

# Run linting
flake8 src/
black src/

# Run migrations
alembic upgrade head
```

### Frontend Development
```bash
# Run web app in development mode
cd web
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Mobile Development
```bash
# Start mobile development
cd mobile
npm start

# Run on specific platform
npm run android
npm run ios
```

### Docker Commands
```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop all services
docker-compose -f docker-compose.dev.yml down

# Restart specific service
docker-compose -f docker-compose.dev.yml restart backend

# Rebuild containers
docker-compose -f docker-compose.dev.yml build --no-cache

# Run tests in container
docker-compose -f docker-compose.dev.yml exec backend pytest
```

## Database Setup

The application uses PostgreSQL as the primary database. The Docker setup will automatically:

1. Create the database containers
2. Run migrations
3. Set up initial schema

### Manual Database Setup

If you need to set up the database manually:

```bash
# Create database
createdb ai_erp_dev

# Run migrations
cd backend
alembic upgrade head

# Create test database
createdb ai_erp_test
```

## Environment Configuration

Key environment variables you may want to configure:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_erp_dev

# Redis
REDIS_URL=redis://localhost:6379

# JWT Security
JWT_SECRET=your-secret-key-change-in-production

# External Services (optional)
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=your-key
STRIPE_SECRET_KEY=sk_test_your-key
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000, 5432, 6379, and 8000 are available
2. **Docker issues**: Restart Docker service and try again
3. **Permission errors**: On Linux/Mac, you may need to run with `sudo`
4. **Database connection**: Ensure PostgreSQL is running and accessible

### Health Checks

- **Backend Health**: http://localhost:8000/health
- **Frontend Health**: http://localhost:3000/health

### Logs

```bash
# View all logs
docker-compose -f docker-compose.dev.yml logs

# View specific service logs
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs web
docker-compose -f docker-compose.dev.yml logs postgres
```

## Next Steps

1. Check out the [API Documentation](http://localhost:8000/docs)
2. Explore the web interface at http://localhost:3000
3. Review the [Contributing Guidelines](CONTRIBUTING.md)
4. Read the [Development Setup](DEV_README.md) for detailed development info

## Support

If you encounter any issues:

1. Check the logs for error messages
2. Ensure all prerequisites are correctly installed
3. Verify your environment configuration
4. Check if all services are running properly

For additional help, please refer to the project documentation or open an issue.

# AI ERP SaaS - Clean Minimal Architecture

A production-ready AI-powered ERP SaaS application with React frontend, FastAPI backend, PostgreSQL database, and dedicated OCR microservice.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Next.js)     │    │   (Python)      │    │   (Primary)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   OCR/AI        │              │
         └──────────────►│   Service       │◄─────────────┘
                        │   (Microservice)│
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd ai-erp-saas-app
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - OCR Service: http://localhost:8001

### Production Deployment

1. **Configure environment:**
   ```bash
   cp production.env.template .env
   # Edit .env with your production values
   ```

2. **Deploy:**
   ```bash
   ./deploy-production.sh
   ```

## 📁 Project Structure

```
ai-erp-saas-app/
├── frontend/                 # React/Next.js frontend
│   ├── src/
│   │   ├── app/             # Next.js 14 app directory
│   │   ├── components/      # Reusable UI components
│   │   ├── lib/            # Utilities and API client
│   │   └── hooks/          # Custom React hooks
│   ├── package.json
│   └── Dockerfile
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── schemas/        # Pydantic schemas
│   ├── requirements.txt
│   └── Dockerfile
├── ocr-service/             # Dedicated OCR microservice
│   ├── src/
│   │   ├── api/            # OCR API endpoints
│   │   ├── services/       # OCR processing logic
│   │   └── models/         # AI/ML models
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
└── README.md
```

## 🛠️ Key Features

### Frontend (React/Next.js)
- **Framework**: Next.js 14 with App Router
- **UI Library**: Radix UI + Tailwind CSS
- **State Management**: React Query for server state
- **Authentication**: JWT tokens with HTTP-only cookies
- **Key Features**: Dashboard, invoice management, OCR upload, analytics

### Backend (FastAPI)
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with refresh tokens
- **API Design**: RESTful with OpenAPI documentation
- **Key Features**: User management, invoice processing, ERP integration

### OCR Service (Microservice)
- **Framework**: FastAPI (lightweight)
- **AI/ML**: Azure Form Recognizer + custom models
- **Processing**: Async document processing
- **Key Features**: Document OCR, data extraction, validation

### Database (PostgreSQL)
- **Primary DB**: PostgreSQL 15
- **Migrations**: Alembic
- **Key Tables**: Users, Companies, Invoices, Audit logs
- **Optimizations**: Indexes, connection pooling, query optimization

## 🔧 Configuration

### Environment Variables

#### Development (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_erp
REDIS_URL=redis://localhost:6379
OCR_SERVICE_URL=http://localhost:8001
SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

#### Production (.env)
```env
POSTGRES_PASSWORD=your-secure-password
SECRET_KEY=your-very-secure-secret-key
CORS_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=your-azure-key
```

## 🧪 Testing

### Run Integration Tests
```bash
node test-integration.js
```

### Run Performance Tests
```bash
node test-performance.js
```

### Run All Tests
```bash
npm test
```

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- OCR Service: `GET /health`
- Frontend: `GET /`

### Metrics
- Prometheus metrics available at `/metrics`
- Response time monitoring
- Error rate tracking
- Resource usage monitoring

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with Sentry integration
- Audit trail for all operations

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
./deploy-production.sh
```

### Manual Production Setup
1. Configure environment variables
2. Build and start services: `docker-compose -f docker-compose.prod.yml up -d`
3. Run migrations: `docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head`
4. Setup SSL certificates
5. Configure monitoring

## 🔒 Security

- JWT authentication with refresh tokens
- Rate limiting per endpoint
- Input validation with Pydantic
- CORS configuration
- Security headers middleware
- SQL injection prevention
- XSS protection
- CSRF protection

## 📈 Performance

- Database connection pooling
- Query optimization with indexes
- Response caching with Redis
- GZIP compression
- CDN-ready static assets
- Horizontal scaling support

## 🛠️ Development

### Adding New Features

1. **Backend API:**
   - Add endpoint in `backend/src/api/v1/endpoints/`
   - Add schema in `backend/src/schemas/`
   - Add service logic in `backend/src/services/`

2. **Frontend:**
   - Add component in `frontend/src/components/`
   - Add page in `frontend/src/app/`
   - Update API client in `frontend/src/lib/api.ts`

3. **OCR Service:**
   - Add processing logic in `ocr-service/src/services/`
   - Add endpoint in `ocr-service/src/main.py`

### Database Migrations

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Open an issue on GitHub
- Contact the development team

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Log aggregation configured
- [ ] Error tracking setup
- [ ] Performance monitoring
- [ ] Security audit completed
- [ ] Load testing completed
- [ ] Documentation updated
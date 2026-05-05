# GitHub Wiki Content for React Login Project

## Home Page

# React Login Application

A secure web application with user authentication, role-based access control, and comprehensive security features.

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.13
- Docker Desktop

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd react

# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### Docker Deployment
```bash
# Build and run with Docker
docker compose up --build
```

Access the application at http://localhost:3000

---

## Installation Guide

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Database is automatically created on first run
   # Test users are pre-configured:
   # - user@gmail.com / 123456 (normal)
   # - admin@gmail.com / admin123 (admin)
   # - guest@gmail.com / guest123 (guest)
   ```

3. **Run Backend Server**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install Node.js Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm start
   ```

### Docker Setup

1. **Install Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop
   - Start Docker Desktop

2. **Build and Run**
   ```bash
   docker compose up --build
   ```

---

## User Guide

### Login Process

1. **Access Application**
   - Open http://localhost:3000 in browser

2. **Enter Credentials**
   - Use test accounts or register new user

3. **User Roles**
   - **Normal User**: Standard access
   - **Admin User**: Administrative privileges
   - **Guest User**: Limited access

### Registration

1. **Register New User**
   - Click registration link
   - Enter email and password
   - Select role (if applicable)

2. **Admin Registration**
   - Use `/admin/create` endpoint
   - Requires admin privileges

### Security Features

- **SQL Injection Protection**: All queries are parameterized
- **Input Validation**: Email and password validation
- **Rate Limiting**: Prevents brute force attacks
- **CORS Security**: Restricted access domains
- **Password Hashing**: SHA256 encryption

---

## API Documentation

### Authentication Endpoints

#### POST /login
Authenticates user credentials.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": "user@example.com",
  "role": "normal"
}
```

#### POST /register
Registers new user account.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "role": "normal"
}
```

#### GET /guest
Provides guest access without authentication.

**Response:**
```json
{
  "success": true,
  "message": "Guest access granted",
  "user": "guest",
  "role": "guest"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### Security Headers

All endpoints include:
- CORS protection
- Input validation
- SQL injection prevention
- Rate limiting

---

## Development Guide

### Project Structure

```
react/
├── backend/                 # Python Flask server
│   ├── app.py              # Main application
│   ├── database.py         # Database configuration
│   ├── models.py           # User models
│   ├── security.py         # Security module
│   ├── rate_limiter.py     # Rate limiting
│   ├── testes/             # Test files
│   └── Dockerfile          # Docker configuration
├── frontend/               # React application
│   ├── src/
│   │   ├── App.js         # Main component
│   │   └── *.test.js      # Test files
│   ├── public/            # Static assets
│   └── Dockerfile         # Docker configuration
├── .github/workflows/     # GitHub Actions
├── docker-compose.yml     # Docker orchestration
└── README.md              # Project documentation
```

### Testing

#### Backend Tests
```bash
cd backend
python testes/test_security.py
python testes/test_database.py
```

#### Frontend Tests
```bash
cd frontend
npm test                    # Unit tests
npm test -- --testPathPattern=integration  # Integration tests
```

#### Security Tests
```bash
# SQL injection protection
# Input validation
# Rate limiting
# CORS configuration
```

### Code Standards

- **Python**: PEP 8 style guide
- **JavaScript**: ESLint configuration
- **Comments**: Portuguese (Portugal)
- **Security**: OWASP guidelines

---

## Deployment Guide

### Docker Deployment

#### Development
```bash
docker compose up --build
```

#### Production
```bash
docker compose -f docker-compose.prod.yml up -d
```

### GitHub Actions

#### CI Pipeline
- **Triggers**: Push to main/devops, Pull requests
- **Tests**: Backend and frontend test suites
- **Build**: Docker image validation
- **Security**: Vulnerability scanning

#### Deployment Pipeline
- **Triggers**: Push to main branch
- **Build**: Docker images
- **Deploy**: Staging environment
- **Tests**: Smoke tests and health checks

### Environment Variables

Create `.env` file:
```env
DOCKER_USERNAME=yourusername
DOCKER_PASSWORD=yourpassword
SLACK_WEBHOOK=your-webhook-url
```

### Monitoring

#### Health Checks
- Backend: `/health` endpoint
- Frontend: HTTP status checks
- Docker: Container health monitoring

#### Logging
- Application logs
- Security events
- Performance metrics

---

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Reset Docker environment
docker compose down -rmi all
docker system prune -a
```

#### Database Issues
```bash
# Reset database
rm backend/users.db
python app.py  # Will recreate database
```

#### Port Conflicts
```bash
# Check port usage
netstat -ano | findstr :3000
netstat -ano | findstr :5000
```

### Debug Mode

#### Backend Debugging
```bash
# Enable debug mode
export FLASK_ENV=development
python app.py
```

#### Frontend Debugging
```bash
# Enable detailed logs
npm start -- --verbose
```

---

## Contributing

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests
   - Update documentation

3. **Test Changes**
   ```bash
   # Run all tests
   npm test
   python testes/test_security.py
   docker compose up --build
   ```

4. **Submit Pull Request**
   - Create PR to main branch
   - Include test results
   - Update documentation

### Code Review Process

1. **Automated Checks**
   - GitHub Actions CI pipeline
   - Security scans
   - Code quality checks

2. **Manual Review**
   - Code style compliance
   - Security best practices
   - Documentation updates

---

## Security

### Implemented Protections

- **SQL Injection**: Parameterized queries
- **XSS Protection**: Input sanitization
- **CSRF Protection**: CORS configuration
- **Rate Limiting**: IP-based request limiting
- **Password Security**: SHA256 hashing
- **Input Validation**: Email and password format checking

### Security Testing

```bash
# Run security tests
python testes/test_security.py

# Test SQL injection protection
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "'\'' OR '\''1'\''='\''1", "password": "password"}'

# Test rate limiting
# Make multiple rapid login attempts
```

### Vulnerability Scanning

- **Trivy**: Container vulnerability scanning
- **OWASP ZAP**: Web application security testing
- **Bandit**: Python security linter

---

## Changelog

### Version 1.0.0
- Initial release
- Basic login functionality
- SQLite database integration
- Security features implemented

### Version 1.1.0
- Docker containerization
- GitHub Actions CI/CD
- Enhanced security testing
- Role-based access control

### Version 1.2.0
- DevOps automation
- Production deployment
- Monitoring and logging
- Performance optimizations

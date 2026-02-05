# BugHunterX Quick Start Guide

## Prerequisites

Before starting, ensure you have:
- Docker (20.10+)
- Docker Compose (2.0+)
- 8GB+ RAM
- 20GB+ disk space
- Git

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/0xyoussef404/DEXTER.git
cd DEXTER
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your favorite editor
```

**Important environment variables:**
```env
# Database passwords (change in production!)
DATABASE_URL=postgresql://bughunterx:CHANGE_THIS_PASSWORD@postgres:5432/bughunterx
MONGO_URL=mongodb://bughunterx:CHANGE_THIS_PASSWORD@mongo:27017/
REDIS_URL=redis://:CHANGE_THIS_PASSWORD@redis:6379/0

# Security (MUST change in production!)
SECRET_KEY=your-super-secret-key-min-32-chars-change-this-now

# Optional: External API keys for enhanced features
VIRUSTOTAL_API_KEY=your_virustotal_key
SHODAN_API_KEY=your_shodan_key
CENSYS_API_ID=your_censys_id
CENSYS_API_SECRET=your_censys_secret
```

### Step 3: Run Installation Script

```bash
# Make script executable (if needed)
chmod +x scripts/install.sh

# Run installation
./scripts/install.sh
```

The script will:
1. Validate Docker installation
2. Create necessary directories
3. Build Docker images
4. Start all services
5. Check service health

### Step 4: Verify Installation

Check that all services are running:

```bash
docker-compose ps
```

You should see:
- ✅ bughunterx-backend (running)
- ✅ bughunterx-postgres (running)
- ✅ bughunterx-mongo (running)
- ✅ bughunterx-redis (running)
- ✅ bughunterx-elasticsearch (running)
- ✅ bughunterx-rabbitmq (running)
- ✅ bughunterx-celery-worker (running)
- ✅ bughunterx-flower (running)

## Access the Platform

### Web Interfaces

- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/api/docs
- **API Documentation (ReDoc)**: http://localhost:8000/api/redoc
- **Flower (Celery Monitoring)**: http://localhost:5555
- **Frontend** (when ready): http://localhost:3000

### Database Access

- **PostgreSQL**: `localhost:5432`
  ```bash
  psql postgresql://bughunterx:bughunterx_secure_pass@localhost:5432/bughunterx
  ```

- **MongoDB**: `localhost:27017`
  ```bash
  mongosh mongodb://bughunterx:bughunterx_secure_pass@localhost:27017/
  ```

- **Redis**: `localhost:6379`
  ```bash
  redis-cli -a bughunterx_secure_pass
  ```

- **Elasticsearch**: http://localhost:9200

- **RabbitMQ Management**: http://localhost:15672
  - Username: `bughunterx`
  - Password: `bughunterx_secure_pass`

## Your First Scan

### Using the API Documentation (Swagger UI)

1. Open http://localhost:8000/api/docs in your browser

2. **Create a Target**:
   ```
   POST /api/v1/targets/
   {
     "url": "https://example.com",
     "domain": "example.com"
   }
   ```
   Note the returned `target_id`

3. **Create a Scan**:
   ```
   POST /api/v1/scans/
   {
     "name": "My First Scan",
     "description": "Testing BugHunterX",
     "target_id": 1,
     "config": {
       "scan_type": "recon",
       "recon": {
         "subdomain_enumeration": true,
         "passive_sources": true,
         "active_enumeration": false,
         "dns_analysis": true,
         "port_scanning": true,
         "tech_detection": true,
         "web_crawling": true,
         "javascript_analysis": true,
         "content_discovery": true,
         "api_discovery": true,
         "parameter_discovery": true,
         "crawl_depth": 3,
         "wordlist_level": "quick"
       }
     }
   }
   ```

4. **Monitor Scan Progress**:
   - Check Flower dashboard: http://localhost:5555
   - Query scan status: `GET /api/v1/scans/{scan_id}`

5. **View Results**:
   - Findings: `GET /api/v1/findings/?scan_id={scan_id}`
   - Recon data: `GET /api/v1/recon/{scan_id}/subdomains`

### Using cURL

```bash
# Create a target
curl -X POST http://localhost:8000/api/v1/targets/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "domain": "example.com"
  }'

# Create a scan (replace target_id with actual ID from above)
curl -X POST http://localhost:8000/api/v1/scans/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Scan",
    "target_id": 1,
    "config": {
      "scan_type": "recon",
      "recon": {
        "subdomain_enumeration": true,
        "passive_sources": true
      }
    }
  }'
```

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart celery-worker
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### Update Code

```bash
# Pull latest changes
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

### Access Service Shells

```bash
# Backend Python shell
docker-compose exec backend python

# PostgreSQL shell
docker-compose exec postgres psql -U bughunterx

# Redis CLI
docker-compose exec redis redis-cli

# Celery worker shell
docker-compose exec celery-worker bash
```

## Troubleshooting

### Services won't start

1. Check Docker resources (RAM/CPU)
2. View logs: `docker-compose logs`
3. Check port conflicts: `netstat -tulpn | grep -E '(5432|27017|6379|9200|5672|8000)'`

### Database connection errors

1. Wait for services to be fully ready (30-60 seconds)
2. Check service health: `docker-compose ps`
3. Verify credentials in `.env` file

### Celery tasks not executing

1. Check RabbitMQ status: http://localhost:15672
2. View worker logs: `docker-compose logs celery-worker`
3. Check Flower dashboard: http://localhost:5555

### Out of memory errors

1. Increase Docker memory limit (Docker Desktop settings)
2. Reduce concurrent workers in `docker-compose.yml`
3. Limit scan concurrency in `.env`

## Development Workflow

### Running in Development Mode

The default setup runs in development mode with:
- Auto-reload on code changes (backend)
- Debug logging
- Verbose error messages
- Direct database access

### Making Code Changes

1. Edit files in `backend/app/`
2. FastAPI will auto-reload
3. Test changes via Swagger UI or cURL
4. View logs: `docker-compose logs -f backend`

### Adding Dependencies

```bash
# Add to backend/requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# Rebuild backend
docker-compose build backend

# Restart
docker-compose up -d backend
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY
- [ ] Disable DEBUG mode
- [ ] Set up HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable authentication
- [ ] Set up backups
- [ ] Configure log rotation
- [ ] Review CORS settings
- [ ] Set up monitoring/alerting

### Production Environment Variables

```env
DEBUG=False
ALLOWED_ORIGINS=["https://your-domain.com"]
SECRET_KEY=generate-a-strong-random-key-here
DATABASE_URL=postgresql://user:secure_password@db_host:5432/bughunterx
```

## Next Steps

1. **Read the Documentation**:
   - [Architecture](./docs/ARCHITECTURE.md)
   - [Phase 1 Implementation](./docs/PHASE1_IMPLEMENTATION.md)

2. **Explore the API**:
   - Open Swagger UI: http://localhost:8000/api/docs
   - Try different endpoints
   - Review request/response schemas

3. **Monitor Tasks**:
   - Open Flower: http://localhost:5555
   - Watch task execution
   - Review task history

4. **Run Test Scans**:
   - Start with reconnaissance-only scans
   - Use test targets (with permission!)
   - Review results in database

5. **Contribute**:
   - Check TODO items in code
   - Implement pending features
   - Submit pull requests

## Getting Help

- **Issues**: https://github.com/0xyoussef404/DEXTER/issues
- **Documentation**: `docs/` directory
- **API Docs**: http://localhost:8000/api/docs

## Legal & Ethical Notice

⚠️ **WARNING**: This tool is designed for **AUTHORIZED SECURITY TESTING ONLY**.

- Only scan systems you own or have explicit written permission to test
- Unauthorized security testing is illegal in most jurisdictions
- Users are solely responsible for compliance with all applicable laws
- This tool is for educational and professional security testing purposes only
- The developers assume no liability for misuse of this software

**By using BugHunterX, you agree to use it responsibly and ethically.**

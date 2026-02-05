# BugHunterX System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              BugHunterX Platform                          │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   Web Dashboard  │         │    CLI Tool      │         │   REST API   │
│   (Next.js 14)   │◄────────┤   (Python)       │◄────────┤   Clients    │
│                  │         │                  │         │              │
└────────┬─────────┘         └────────┬─────────┘         └──────┬───────┘
         │                            │                           │
         │                            ▼                           │
         │                   ┌─────────────────┐                 │
         └──────────────────►│  FastAPI Backend │◄───────────────┘
                             │  (Python 3.11+)  │
                             └────────┬─────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   PostgreSQL    │         │   MongoDB       │         │   Redis         │
│  (Main DB)      │         │ (Logs/Raw Data) │         │ (Cache/Queue)   │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Elasticsearch   │         │   RabbitMQ      │         │  Celery Workers │
│ (Analytics)     │         │ (Message Queue) │◄────────┤  (Distributed)  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                                                  │
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │ Security Tools  │
                                                         │ (Nmap, SQLMap,  │
                                                         │  Subfinder...)  │
                                                         └─────────────────┘
```

## Component Details

### Frontend Layer

**Next.js 14 Web Dashboard**
- React 18 with TypeScript
- TailwindCSS + shadcn/ui for UI components
- Recharts + D3.js for data visualization
- Monaco Editor for code/payload editing
- Xterm.js for terminal emulation
- Socket.io client for real-time updates

**Features:**
- Real-time scan progress monitoring
- Interactive vulnerability dashboards
- Detailed finding reports with proof
- Scan configuration management
- User management and RBAC
- Report export (PDF, JSON, HTML)

### Backend Layer

**FastAPI Application (app/main.py)**
- Async/await support for high performance
- Auto-generated OpenAPI documentation
- WebSocket support for real-time updates
- CORS middleware for frontend integration
- Request/response compression (GZip)

**Core Components:**
- `app/core/config.py`: Application configuration
- `app/core/logging.py`: Centralized logging
- `app/db/`: Database connection managers
- `app/models/`: SQLAlchemy ORM models
- `app/schemas/`: Pydantic request/response schemas
- `app/api/v1/`: REST API endpoints

**API Endpoints:**
```
/api/v1/auth      - Authentication (login, register, refresh)
/api/v1/users     - User management
/api/v1/targets   - Target CRUD operations
/api/v1/scans     - Scan management and execution
/api/v1/findings  - Vulnerability findings
/api/v1/recon     - Reconnaissance results
```

### Service Layer

**Reconnaissance Services (app/services/recon/)**
```
subdomain_enum.py    - Subdomain enumeration (15+ sources)
dns_analyzer.py      - DNS record analysis & CDN detection
port_scanner.py      - Port scanning & service detection
tech_detector.py     - Technology stack identification
web_crawler.py       - Deep web crawling with JS rendering
js_analyzer.py       - JavaScript analysis & secret extraction
content_discovery.py - Directory/file brute-forcing
api_discovery.py     - REST/GraphQL API discovery
param_discovery.py   - Hidden parameter discovery
```

**Vulnerability Services (app/services/vuln/)**
```
xss_detector.py      - XSS detection (multi-context)
sqli_detector.py     - SQL injection detection
ssrf_detector.py     - SSRF detection
fuzzer.py            - Advanced fuzzing engine
```

**ML Services (app/services/ml/)**
```
false_positive_filter.py - ML-based FP reduction
adaptive_fuzzer.py       - Intelligent payload generation
```

### Task Queue Layer

**Celery Workers (app/tasks/)**
```
celery_app.py        - Celery configuration
scan_tasks.py        - Main scan orchestration
recon_tasks.py       - Reconnaissance task execution
vuln_tasks.py        - Vulnerability scanning tasks
```

**Task Flow:**
```
1. User initiates scan via API
2. Scan record created in PostgreSQL
3. Celery task dispatched to RabbitMQ
4. Worker picks up task
5. Executes reconnaissance modules
6. Stores results in PostgreSQL/MongoDB
7. Executes vulnerability modules
8. Stores findings in PostgreSQL
9. Updates scan status
10. Sends WebSocket notification to frontend
```

### Database Layer

**PostgreSQL (Main Database)**
- Users and authentication
- Scan metadata and status
- Findings and vulnerabilities
- Target information

**MongoDB (Document Store)**
- Raw scan data
- Log entries
- Large JSON payloads
- Historical data

**Redis (Cache & Queue)**
- Session storage
- API response caching
- Rate limiting counters
- Real-time scan status
- WebSocket pub/sub

**Elasticsearch (Search & Analytics)**
- Full-text search across findings
- Advanced filtering and aggregation
- Trend analysis
- Performance metrics

### Message Queue

**RabbitMQ**
- Task distribution to workers
- Priority queues (scans, recon, vuln)
- Dead letter queues for failed tasks
- Task result storage

## Data Flow

### Scan Execution Flow

```
1. Frontend → Create Scan Request
   POST /api/v1/scans
   {
     "name": "Example.com Scan",
     "target_id": 123,
     "config": {
       "scan_type": "full",
       "recon": {...},
       "vuln": {...}
     }
   }

2. Backend → Validate & Create DB Record
   - Validate target permissions
   - Create scan record in PostgreSQL
   - Generate task ID

3. Backend → Dispatch Celery Task
   - Send task to RabbitMQ
   - Return scan ID to frontend

4. Celery Worker → Execute Scan
   Phase 1: Reconnaissance
   - Subdomain enumeration → MongoDB
   - DNS analysis → MongoDB
   - Port scanning → MongoDB
   - Technology detection → MongoDB
   - Web crawling → MongoDB
   - JS analysis → MongoDB
   - Content discovery → MongoDB
   - API discovery → MongoDB
   - Parameter discovery → MongoDB
   
   Phase 2: Vulnerability Assessment
   - XSS detection → PostgreSQL (findings)
   - SQLi detection → PostgreSQL (findings)
   - SSRF detection → PostgreSQL (findings)
   - Advanced fuzzing → PostgreSQL (findings)

5. Worker → Update Progress
   - Update scan status in PostgreSQL
   - Update progress percentage
   - Send WebSocket updates to frontend

6. Worker → Complete Scan
   - Mark scan as completed
   - Calculate summary statistics
   - Store final results
   - Generate report

7. Frontend → Display Results
   - Real-time progress updates via WebSocket
   - Display findings dashboard
   - Show reconnaissance data
   - Export reports
```

## Security Architecture

### Authentication & Authorization

**JWT-based Authentication:**
- Access tokens (1 hour expiry)
- Refresh tokens (7 days expiry)
- Token stored in HTTP-only cookies

**OAuth2 Integration:**
- Support for Google, GitHub, Microsoft
- Social login for ease of access

**API Keys:**
- Long-lived tokens for CLI/API access
- Per-user API key generation
- Rate limiting per API key

**RBAC (Role-Based Access Control):**
- Admin: Full access
- Analyst: Scan execution, view results
- Viewer: Read-only access

### Data Security

- Passwords: bcrypt hashing
- Sensitive data: Encryption at rest
- API keys: Stored in environment variables
- Database: Connection over SSL/TLS
- Communication: HTTPS only in production

## Scalability Architecture

### Horizontal Scaling

**Web Tier:**
- Multiple FastAPI instances behind load balancer
- Session stored in Redis (shared state)

**Worker Tier:**
- Auto-scaling Celery workers based on queue length
- Dedicated workers for different task types
- Worker pools for CPU/IO bound tasks

**Database Tier:**
- PostgreSQL: Master-replica setup
- MongoDB: Sharded cluster
- Redis: Sentinel for HA
- Elasticsearch: Multi-node cluster

### Performance Optimization

**Caching Strategy:**
- API responses: Redis (5-60 minutes)
- Static data: CDN caching
- Database queries: Result caching

**Async Processing:**
- All I/O operations use async/await
- Connection pooling for databases
- Batch operations where possible

**Rate Limiting:**
- Per-user: 60 requests/minute
- Per-IP: 100 requests/minute
- Scan throttling per target

## Monitoring & Observability

**Application Monitoring:**
- Flower: Celery task monitoring
- FastAPI metrics: Prometheus endpoint
- Custom metrics: Scan success rate, finding detection

**Logging:**
- Centralized logging to Elasticsearch
- Log levels: DEBUG, INFO, WARNING, ERROR
- Structured logging (JSON format)

**Alerting:**
- Failed scans notification
- System health alerts
- Resource usage alerts

## Deployment Architecture

### Development
```
docker-compose up
```

### Production
```
Kubernetes cluster with:
- Ingress controller (NGINX)
- FastAPI pods (3+ replicas)
- Celery worker pods (auto-scaling)
- Database StatefulSets
- Redis cluster
- RabbitMQ cluster
```

## Technology Decisions

### Why FastAPI?
- Native async/await support
- Automatic API documentation
- Type hints & validation
- High performance
- Modern Python features

### Why Celery?
- Mature task queue system
- Excellent monitoring (Flower)
- Flexible routing
- Retry mechanisms
- Distributed task execution

### Why Next.js?
- Server-side rendering
- API routes
- Built-in optimization
- Great developer experience
- TypeScript support

### Why PostgreSQL + MongoDB?
- PostgreSQL: ACID compliance for critical data
- MongoDB: Flexible schema for varying recon data
- Best of both worlds approach

## Future Enhancements

1. **Machine Learning**
   - False positive reduction
   - Adaptive fuzzing
   - Vulnerability prediction

2. **Advanced Features**
   - Custom payload creation
   - Automated exploit generation
   - Integration with bug bounty platforms

3. **Scalability**
   - Kubernetes operator
   - Multi-region deployment
   - Edge computing for distributed scans

4. **Integrations**
   - Slack/Discord notifications
   - Jira issue creation
   - GitHub security advisories
   - Integration with SIEM systems

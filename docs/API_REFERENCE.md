# BugHunterX API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

### JWT Authentication (Coming Soon)

```bash
# Login
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "password123"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use token in requests
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### API Key Authentication (Coming Soon)

```bash
X-API-Key: your-api-key-here
```

## Endpoints

### Health Check

**Check API health status**

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "BugHunterX"
}
```

---

### Targets

#### Create Target

```http
POST /api/v1/targets/
Content-Type: application/json

{
  "url": "https://example.com",
  "domain": "example.com",
  "ip_address": "93.184.216.34"  // optional
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "url": "https://example.com",
  "domain": "example.com",
  "ip_address": "93.184.216.34",
  "is_active": true,
  "created_at": "2024-02-05T10:00:00Z",
  "updated_at": null
}
```

#### List Targets

```http
GET /api/v1/targets/?skip=0&limit=100
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "url": "https://example.com",
    "domain": "example.com",
    "ip_address": "93.184.216.34",
    "is_active": true,
    "created_at": "2024-02-05T10:00:00Z"
  }
]
```

#### Get Target

```http
GET /api/v1/targets/{target_id}
```

#### Delete Target

```http
DELETE /api/v1/targets/{target_id}
```

**Response:** `204 No Content`

---

### Scans

#### Create Scan

```http
POST /api/v1/scans/
Content-Type: application/json

{
  "name": "Example.com Full Scan",
  "description": "Comprehensive security assessment",
  "target_id": 1,
  "config": {
    "scan_type": "full",  // "recon", "vuln", or "full"
    "recon": {
      "subdomain_enumeration": true,
      "passive_sources": true,
      "active_enumeration": false,
      "subdomain_takeover": true,
      "dns_analysis": true,
      "port_scanning": true,
      "top_ports": true,
      "full_port_scan": false,
      "service_detection": true,
      "tech_detection": true,
      "web_crawling": true,
      "crawl_depth": 3,
      "javascript_analysis": true,
      "content_discovery": true,
      "wordlist_level": "standard",  // "quick", "standard", or "deep"
      "api_discovery": true,
      "parameter_discovery": true
    },
    "vuln": {
      "xss_detection": true,
      "xss_contexts": ["html", "attribute", "javascript", "url"],
      "sqli_detection": true,
      "sqli_level": 3,
      "sqli_risk": 2,
      "ssrf_detection": true,
      "command_injection": true,
      "xxe_detection": true,
      "path_traversal": true,
      "ssti_detection": true,
      "fuzzing_enabled": true,
      "fuzzing_threads": 50,
      "waf_bypass": true
    },
    "timeout_hours": 24,
    "max_threads": 10,
    "rate_limit": 10,  // requests per second
    "user_agent": "Mozilla/5.0...",  // optional
    "custom_headers": {  // optional
      "X-Custom-Header": "value"
    },
    "cookies": {  // optional
      "session": "abc123"
    },
    "proxy": "http://proxy:8080"  // optional
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Example.com Full Scan",
  "description": "Comprehensive security assessment",
  "target_id": 1,
  "config": {...},
  "status": "pending",
  "progress": 0.0,
  "current_phase": null,
  "started_at": null,
  "completed_at": null,
  "created_at": "2024-02-05T10:00:00Z",
  "updated_at": null,
  "total_findings": 0,
  "critical_count": 0,
  "high_count": 0,
  "medium_count": 0,
  "low_count": 0,
  "info_count": 0,
  "task_id": "celery-task-uuid"
}
```

#### List Scans

```http
GET /api/v1/scans/?skip=0&limit=100&status=running
```

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Max results (default: 100)
- `status`: Filter by status (pending, running, completed, failed, cancelled)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Example.com Full Scan",
    "status": "running",
    "progress": 45.5,
    "target_url": "https://example.com",
    "started_at": "2024-02-05T10:00:00Z",
    "completed_at": null,
    "total_findings": 12,
    "critical_count": 2,
    "high_count": 5,
    "medium_count": 3,
    "low_count": 2
  }
]
```

#### Get Scan

```http
GET /api/v1/scans/{scan_id}
```

**Response:** `200 OK` (Full scan object)

#### Update Scan

```http
PUT /api/v1/scans/{scan_id}
Content-Type: application/json

{
  "name": "Updated Scan Name",
  "description": "Updated description",
  "status": "cancelled"
}
```

#### Stop Scan

```http
POST /api/v1/scans/{scan_id}/stop
```

**Response:** `200 OK`

#### Delete Scan

```http
DELETE /api/v1/scans/{scan_id}
```

**Response:** `204 No Content`

#### Generate Report

```http
GET /api/v1/scans/{scan_id}/report?format=json
```

**Query Parameters:**
- `format`: Report format (json, pdf, html)

---

### Findings

#### List Findings

```http
GET /api/v1/findings/?scan_id=1&severity=high&vulnerability_type=xss
```

**Query Parameters:**
- `scan_id`: Filter by scan
- `severity`: Filter by severity (critical, high, medium, low, info)
- `vulnerability_type`: Filter by type (xss, sqli, ssrf, etc.)
- `skip`: Pagination offset
- `limit`: Max results

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "scan_id": 1,
    "title": "Reflected XSS in search parameter",
    "description": "The search parameter reflects user input without sanitization...",
    "vulnerability_type": "xss",
    "severity": "high",
    "confidence": 0.95,
    "url": "https://example.com/search",
    "parameter": "q",
    "method": "GET",
    "payload": "<script>alert(1)</script>",
    "request": "GET /search?q=<script>alert(1)</script> HTTP/1.1\n...",
    "response": "HTTP/1.1 200 OK\n...",
    "proof": {
      "screenshot": "base64_image_data",
      "execution_confirmed": true
    },
    "cvss_score": 7.3,
    "cwe_id": "CWE-79",
    "owasp_category": "A03:2021 – Injection",
    "remediation": "Sanitize and encode user input before reflecting in HTML context...",
    "references": [
      "https://owasp.org/www-community/attacks/xss/",
      "https://cwe.mitre.org/data/definitions/79.html"
    ],
    "is_false_positive": false,
    "is_verified": true,
    "notes": null,
    "created_at": "2024-02-05T10:30:00Z"
  }
]
```

#### Get Finding

```http
GET /api/v1/findings/{finding_id}
```

#### Update Finding

```http
PUT /api/v1/findings/{finding_id}
Content-Type: application/json

{
  "is_false_positive": true,
  "is_verified": false,
  "notes": "This is a false positive because..."
}
```

#### Delete Finding

```http
DELETE /api/v1/findings/{finding_id}
```

---

### Reconnaissance Results

#### Get Subdomains

```http
GET /api/v1/recon/{scan_id}/subdomains
```

**Response:** `200 OK`
```json
{
  "scan_id": 1,
  "subdomains": [
    {
      "subdomain": "www.example.com",
      "source": "crt.sh",
      "confidence": 0.9,
      "takeover_vulnerable": false,
      "ip_addresses": ["93.184.216.34"],
      "cname": null
    },
    {
      "subdomain": "api.example.com",
      "source": "dns_bruteforce",
      "confidence": 1.0,
      "takeover_vulnerable": false,
      "ip_addresses": ["93.184.216.35"]
    }
  ],
  "total_count": 2
}
```

#### Get Ports

```http
GET /api/v1/recon/{scan_id}/ports
```

**Response:** `200 OK`
```json
{
  "scan_id": 1,
  "hosts": [
    {
      "host": "93.184.216.34",
      "ports": [
        {
          "port": 80,
          "protocol": "tcp",
          "state": "open",
          "service": "http",
          "version": "nginx 1.21.0",
          "banner": "nginx/1.21.0"
        },
        {
          "port": 443,
          "protocol": "tcp",
          "state": "open",
          "service": "https",
          "version": "nginx 1.21.0",
          "ssl_info": {
            "subject": "CN=example.com",
            "issuer": "CN=Let's Encrypt",
            "valid_from": "2024-01-01",
            "valid_to": "2024-04-01"
          }
        }
      ]
    }
  ]
}
```

#### Get Technologies

```http
GET /api/v1/recon/{scan_id}/technologies
```

**Response:** `200 OK`
```json
{
  "scan_id": 1,
  "technologies": {
    "web_servers": ["Nginx 1.21.0"],
    "frameworks": ["React 18.2.0", "Next.js 14.0.0"],
    "cms": [],
    "programming_languages": ["JavaScript", "TypeScript"],
    "cdn": ["Cloudflare"],
    "waf": ["Cloudflare WAF"],
    "analytics": ["Google Analytics"],
    "libraries": [
      {
        "name": "jQuery",
        "version": "3.6.0",
        "vulnerabilities": []
      }
    ]
  }
}
```

#### Get Endpoints

```http
GET /api/v1/recon/{scan_id}/endpoints
```

#### Get Parameters

```http
GET /api/v1/recon/{scan_id}/parameters
```

#### Get All Recon Results

```http
GET /api/v1/recon/{scan_id}/results?recon_type=subdomain
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message",
  "error": "Detailed error information (debug mode only)"
}
```

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success, no response body
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `501 Not Implemented` - Feature not yet implemented
- `503 Service Unavailable` - Service temporarily unavailable

---

## Rate Limiting

**Limits:**
- Authenticated users: 60 requests/minute
- Unauthenticated: 30 requests/minute
- Scan creation: 10 scans/hour

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1612540800
```

---

## WebSocket API (Coming Soon)

### Real-time Scan Updates

```javascript
const socket = io('ws://localhost:8000');

socket.on('connect', () => {
  socket.emit('subscribe', { scan_id: 1 });
});

socket.on('scan_update', (data) => {
  console.log('Progress:', data.progress);
  console.log('Phase:', data.current_phase);
  console.log('Status:', data.status);
});

socket.on('finding_discovered', (finding) => {
  console.log('New finding:', finding);
});
```

---

## SDK Examples

### Python

```python
import requests

base_url = "http://localhost:8000/api/v1"

# Create target
target_response = requests.post(
    f"{base_url}/targets/",
    json={
        "url": "https://example.com",
        "domain": "example.com"
    }
)
target_id = target_response.json()["id"]

# Create scan
scan_response = requests.post(
    f"{base_url}/scans/",
    json={
        "name": "My Scan",
        "target_id": target_id,
        "config": {
            "scan_type": "recon",
            "recon": {
                "subdomain_enumeration": True,
                "passive_sources": True
            }
        }
    }
)
scan_id = scan_response.json()["id"]

# Get scan status
status_response = requests.get(f"{base_url}/scans/{scan_id}")
print(status_response.json())
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const baseUrl = 'http://localhost:8000/api/v1';

async function runScan() {
  // Create target
  const targetResponse = await axios.post(`${baseUrl}/targets/`, {
    url: 'https://example.com',
    domain: 'example.com'
  });
  const targetId = targetResponse.data.id;

  // Create scan
  const scanResponse = await axios.post(`${baseUrl}/scans/`, {
    name: 'My Scan',
    target_id: targetId,
    config: {
      scan_type: 'recon',
      recon: {
        subdomain_enumeration: true,
        passive_sources: true
      }
    }
  });
  const scanId = scanResponse.data.id;

  // Get scan status
  const statusResponse = await axios.get(`${baseUrl}/scans/${scanId}`);
  console.log(statusResponse.data);
}

runScan();
```

---

## Interactive API Documentation

Visit http://localhost:8000/api/docs for interactive Swagger UI where you can:
- Browse all endpoints
- Try API calls directly
- View request/response schemas
- See example payloads

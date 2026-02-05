# Phase 1: Reconnaissance Engine Implementation Guide

## Overview

This document details the implementation roadmap for BugHunterX Phase 1: Reconnaissance Engine.

## Architecture

The reconnaissance engine is built as a distributed system using:
- **Celery Tasks**: Async task execution
- **Service Layer**: Business logic and tool integration
- **Database Layer**: Results storage in PostgreSQL/MongoDB
- **Queue System**: RabbitMQ for task distribution

## Implementation Status

### ✅ Completed Components

1. **Project Structure**
   - Multi-tier architecture setup
   - Docker infrastructure (PostgreSQL, MongoDB, Redis, Elasticsearch, RabbitMQ)
   - FastAPI backend with async support
   - Celery task orchestration
   - Database models and schemas

2. **Service Architecture**
   - Subdomain enumeration service structure
   - DNS analyzer structure
   - Port scanner structure
   - Technology detector structure
   - Web crawler structure
   - JavaScript analyzer structure
   - Content discovery structure
   - API discovery structure
   - Parameter discovery structure

### 🚧 Pending Implementations

Each service needs tool integrations and logic implementation:

#### 1. Subdomain Enumeration (`app/services/recon/subdomain_enum.py`)

**Passive Sources** (15+):
- ✅ crt.sh API integration (basic implementation)
- ✅ ThreatCrowd API integration (basic implementation)
- ⏳ Censys API (requires API key)
- ⏳ VirusTotal API (requires API key)
- ⏳ SecurityTrails API (requires API key)
- ⏳ Shodan API (requires API key)
- ⏳ Google Transparency Report
- ⏳ Wayback Machine API
- ⏳ urlscan.io API
- ⏳ Chaos ProjectDiscovery
- ⏳ AlienVault OTX
- ⏳ GitHub subdomain search

**Active Enumeration**:
- ⏳ DNS Bruteforce (MassDNS/PureDNS)
- ⏳ Subdomain permutations (Altdns, DNSGen style)
- ⏳ Zone transfer attempts
- ⏳ Reverse DNS lookups

**Tool Integrations**:
- ⏳ Subfinder
- ⏳ Amass
- ⏳ Assetfinder
- ⏳ Findomain

**Detection**:
- ⏳ Subdomain takeover (40+ providers: GitHub, Heroku, S3, Azure, etc.)

#### 2. DNS Analysis (`app/services/recon/dns_analyzer.py`)

**DNS Records**:
- ⏳ A, AAAA, CNAME, MX, TXT, NS, SOA, CAA resolution
- ⏳ DNSSEC validation
- ⏳ DNS history tracking

**Detection**:
- ⏳ CDN detection (Cloudflare, Akamai, Fastly, AWS CloudFront)
- ⏳ WAF detection
- ⏳ Origin IP discovery

#### 3. Port Scanning (`app/services/recon/port_scanner.py`)

**Tool Integrations**:
- ⏳ Nmap (full TCP/UDP + NSE scripts)
- ⏳ Masscan (ultra-fast)
- ⏳ RustScan

**Features**:
- ⏳ Service version detection
- ⏳ OS fingerprinting
- ⏳ Banner grabbing
- ⏳ SSL/TLS certificate analysis

#### 4. Technology Detection (`app/services/recon/tech_detector.py`)

**Tool Integrations**:
- ⏳ Wappalyzer
- ⏳ WhatWeb
- ⏳ Webanalyze
- ⏳ Retire.js (JavaScript libraries)

**CMS Detection**:
- ⏳ WPScan (WordPress)
- ⏳ Joomscan (Joomla)
- ⏳ Drupal scanner

**WAF Detection**:
- ⏳ wafw00f (50+ WAF signatures)

#### 5. Web Crawling (`app/services/recon/web_crawler.py`)

**Crawler Integrations**:
- ⏳ Katana
- ⏳ GoSpider
- ⏳ Hakrawler
- ⏳ Gospider

**Features**:
- ⏳ Headless Chrome/Firefox (JavaScript rendering)
- ⏳ Form detection
- ⏳ Parameter extraction
- ⏳ Link extraction
- ⏳ Configurable depth (3-5 levels)

#### 6. JavaScript Analysis (`app/services/recon/js_analyzer.py`) - CRITICAL

**Tool Integrations**:
- ⏳ LinkFinder
- ⏳ JSParser
- ⏳ SecretFinder
- ⏳ Subjs
- ⏳ relative-url-extractor

**Detection Patterns** (50+):
- ⏳ API endpoints
- ⏳ Subdomains in JS
- ⏳ Parameters
- ⏳ API keys (AWS, Google, Slack, GitHub, etc.)
- ⏳ JWT tokens
- ⏳ Private keys
- ⏳ Database URLs
- ⏳ Internal paths
- ⏳ Comments with sensitive info

**Processing**:
- ⏳ Beautify minified JavaScript
- ⏳ Deobfuscation attempts
- ⏳ Webpack bundle analysis
- ⏳ Source map extraction

#### 7. Content Discovery (`app/services/recon/content_discovery.py`)

**Tool Integrations**:
- ⏳ ffuf (100 threads, auto-calibration, recursion)
- ⏳ feroxbuster (auto-tune, smart filtering)
- ⏳ dirsearch
- ⏳ gobuster

**Wordlist Strategy**:
- ⏳ Quick scan (2-5 min): raft-small, common.txt
- ⏳ Standard scan (15-30 min): directory-list-medium
- ⏳ Deep scan (1-2h): directory-list-big
- ⏳ Tech-specific: WordPress, Joomla, Laravel, Django, Node.js

**Sensitive Files**:
- ⏳ Backups: .bak, .old, .backup, .swp
- ⏳ Compressed: .zip, .tar, backup.sql
- ⏳ Config: .env, config.php, web.config, database.yml
- ⏳ VCS: .git/config, .svn/entries
- ⏳ Misc: .DS_Store, phpinfo.php, robots.txt

#### 8. API Discovery (`app/services/recon/api_discovery.py`)

**Detection**:
- ⏳ API paths (/api/v1, /api/v2, /rest, /graphql)
- ⏳ Swagger/OpenAPI endpoints
- ⏳ API documentation files

**Parsing**:
- ⏳ Swagger/OpenAPI spec extraction
- ⏳ GraphQL introspection (if enabled)
- ⏳ WADL/WSDL detection and parsing

#### 9. Parameter Discovery (`app/services/recon/param_discovery.py`)

**Tool Integrations**:
- ⏳ Arjun (adaptive learning)
- ⏳ ParamSpider (archive mining)
- ⏳ x8 (bruteforce + discovery)

**Parameter Patterns**:
- ⏳ Common: id, user, page, search, query, file
- ⏳ API-specific: limit, offset, sort, filter
- ⏳ Injection-prone: cmd, exec, sql, query

## Implementation Priority

### Phase 1.1 (Critical - Week 1-2)
1. ✅ Project setup and infrastructure
2. Subdomain enumeration (passive sources first)
3. Basic DNS analysis
4. JavaScript analysis (secret detection)

### Phase 1.2 (High Priority - Week 3-4)
1. Web crawling with JS rendering
2. Content discovery (ffuf/feroxbuster)
3. API discovery
4. Parameter discovery

### Phase 1.3 (Medium Priority - Week 5-6)
1. Port scanning (Nmap integration)
2. Technology detection
3. Active subdomain enumeration
4. Subdomain takeover detection

### Phase 1.4 (Enhancement - Week 7-8)
1. External tool integrations (Subfinder, Amass)
2. Advanced DNS analysis
3. Historical data mining
4. Performance optimization

## Tool Installation Guide

### Security Tools to Install

```bash
# Go-based tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/hakluke/hakrawler@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest

# Python tools
pip install arjun
pip install sqlmap

# ffuf (directory bruteforcer)
wget https://github.com/ffuf/ffuf/releases/latest/download/ffuf_2.1.0_linux_amd64.tar.gz
tar -xzf ffuf_2.1.0_linux_amd64.tar.gz
mv ffuf /usr/local/bin/

# Nmap (usually pre-installed)
apt-get install nmap

# Masscan
apt-get install masscan

# WPScan
gem install wpscan

# wafw00f
pip install wafw00f
```

### Wordlists

```bash
# SecLists - comprehensive wordlists
git clone https://github.com/danielmiessler/SecLists.git wordlists/SecLists

# Directory lists
wget https://raw.githubusercontent.com/raft-project/raft/master/data/small.txt -O wordlists/raft-small.txt
wget https://raw.githubusercontent.com/raft-project/raft/master/data/large.txt -O wordlists/raft-large.txt
```

## Testing

Each service should include:
1. Unit tests for core logic
2. Integration tests with mock tools
3. End-to-end tests with real targets (test domains)

## Performance Considerations

- Use async/await for I/O operations
- Implement connection pooling
- Add rate limiting per target
- Cache API responses (Redis)
- Use bulk database operations
- Implement timeout handling
- Add retry logic with exponential backoff

## Security Considerations

- Validate all user inputs
- Sanitize target domains
- Implement scope verification
- Add authorization checks
- Store API keys securely (environment variables)
- Log all scanning activities
- Implement rate limiting
- Add CAPTCHA for public instances

## Next Steps

1. Start implementing passive subdomain enumeration sources
2. Set up unit testing framework
3. Create integration tests
4. Document API usage for each external service
5. Create tool installation automation script

## Resources

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Bug Bounty Methodology](https://github.com/jhaddix/tbhm)
- [HackerOne Reports](https://hackerone.com/hacktivity)

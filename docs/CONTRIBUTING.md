# Contributing to BugHunterX

Thank you for your interest in contributing to BugHunterX! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Use BugHunterX responsibly and ethically
- Only test systems you own or have explicit permission to test
- Report security vulnerabilities responsibly

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs/screenshots

### Suggesting Features

1. Open an issue with the feature request template
2. Describe:
   - The problem it solves
   - Proposed solution
   - Alternative approaches considered
   - Implementation details (if applicable)

### Submitting Code

#### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/DEXTER.git
cd DEXTER

# Create a feature branch
git checkout -b feature/my-new-feature

# Start development environment
docker-compose up -d

# Make your changes
# Test your changes

# Commit and push
git add .
git commit -m "Add feature: description"
git push origin feature/my-new-feature

# Open a pull request
```

#### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Max line length: 100 characters

```python
def enumerate_subdomains(domain: str, config: Dict[str, Any]) -> List[str]:
    """
    Enumerate subdomains for the given domain.
    
    Args:
        domain: The target domain
        config: Configuration dictionary
        
    Returns:
        List of discovered subdomains
        
    Raises:
        ValueError: If domain is invalid
    """
    pass
```

**TypeScript/JavaScript:**
- Use ESLint and Prettier
- Prefer functional components (React)
- Use TypeScript for type safety
- Write JSDoc comments

#### Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Test with different configurations
- Include integration tests

```bash
# Run tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

#### Pull Request Process

1. **Before submitting:**
   - Update documentation
   - Add tests
   - Run linters
   - Test locally
   - Update CHANGELOG.md

2. **PR Description:**
   - Clear title
   - Detailed description
   - Link related issues
   - Include screenshots (UI changes)
   - List breaking changes

3. **Review Process:**
   - Automated tests must pass
   - Code review approval required
   - Address review feedback
   - Squash commits if requested

## Development Guidelines

### Project Structure

```
DEXTER/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core config
│   │   ├── db/          # Database
│   │   ├── models/      # ORM models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── tasks/       # Celery tasks
│   │   └── utils/       # Utilities
│   └── tests/           # Backend tests
├── frontend/            # Next.js frontend
├── docs/                # Documentation
└── scripts/             # Utility scripts
```

### Adding a New Reconnaissance Module

1. **Create service file:**
   ```python
   # backend/app/services/recon/my_module.py
   
   class MyReconModule:
       def __init__(self, scan_id: int):
           self.scan_id = scan_id
       
       def execute(self) -> Dict:
           """Execute reconnaissance"""
           pass
   ```

2. **Create Celery task:**
   ```python
   # backend/app/tasks/recon_tasks.py
   
   @celery_app.task(name="app.tasks.recon_tasks.my_module_task")
   def my_module_task(scan_id: int, config: dict):
       from app.services.recon.my_module import MyReconModule
       module = MyReconModule(scan_id)
       return module.execute()
   ```

3. **Add to orchestration:**
   ```python
   # In execute_recon_scan task
   results["my_module"] = my_module_task.apply_async(
       args=[scan_id, config]
   ).get()
   ```

4. **Write tests:**
   ```python
   # backend/tests/test_my_module.py
   
   def test_my_module():
       module = MyReconModule(1)
       result = module.execute()
       assert result is not None
   ```

5. **Update documentation:**
   - Add to README.md
   - Document in PHASE1_IMPLEMENTATION.md
   - Update API_REFERENCE.md if needed

### Adding a New Vulnerability Module

Similar process to reconnaissance modules, but in:
- `backend/app/services/vuln/`
- `backend/app/tasks/vuln_tasks.py`

### Database Migrations

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Run migration
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1
```

### Tool Integration Guidelines

When integrating external security tools:

1. **Containerize when possible:**
   ```dockerfile
   # Install tool in Dockerfile
   RUN go install github.com/tool/cmd@latest
   ```

2. **Handle errors gracefully:**
   ```python
   try:
       result = subprocess.run(['tool', 'args'], 
                             capture_output=True, 
                             timeout=300)
   except subprocess.TimeoutExpired:
       logger.error("Tool timed out")
   except Exception as e:
       logger.error(f"Tool failed: {e}")
   ```

3. **Parse output consistently:**
   ```python
   def parse_tool_output(output: str) -> List[Dict]:
       """Parse tool output to standard format"""
       pass
   ```

4. **Add configuration options:**
   ```python
   # In config.py
   TOOL_TIMEOUT: int = 300
   TOOL_THREADS: int = 10
   ```

## Priority Areas

We especially welcome contributions in:

1. **Tool Integrations:**
   - Subfinder, Amass, Assetfinder
   - Nmap, Masscan
   - ffuf, feroxbuster
   - SQLMap, Dalfox, XSStrike

2. **Frontend Development:**
   - Next.js dashboard
   - Real-time updates
   - Data visualizations
   - Report generation

3. **ML/AI Features:**
   - False positive filtering
   - Adaptive fuzzing
   - Pattern recognition

4. **Testing:**
   - Unit tests
   - Integration tests
   - E2E tests

5. **Documentation:**
   - API documentation
   - Tutorials
   - Use cases
   - Video guides

## Community

- **Discussions:** GitHub Discussions
- **Issues:** GitHub Issues
- **Updates:** Watch the repository

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to open an issue with the "question" label or start a discussion.

Thank you for contributing to BugHunterX! 🎯

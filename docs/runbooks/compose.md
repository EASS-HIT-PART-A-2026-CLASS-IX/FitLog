# Docker Compose Runbook

## Quick Start

### 1. Prerequisites

```bash
# Install Docker & Docker Compose
# https://docs.docker.com/get-docker/
# https://docs.docker.com/compose/install/

# Verify installation
docker --version
docker compose version
```

### 2. Configure Environment

Create `.env` file in project root:

```bash
# .env
GEMINI_API_KEY=your-google-gemini-api-key
SECRET_KEY=your-secret-key-$(date +%s)
DATABASE_URL=postgresql+asyncpg://fitlog:fitlog_password@postgres:5432/fitlog
REDIS_URL=redis://redis:6379/0
```

### 3. Start Services

```bash
# Start all services in detached mode
docker compose up -d

# Check status
docker compose ps

# Output:
# NAME             IMAGE              STATUS              PORTS
# fitlog-api       fitlog:latest      Up 2 minutes        0.0.0.0:8000->8000/tcp
# fitlog-postgres  postgres:16        Up 2 minutes        0.0.0.0:5432->5432/tcp
# fitlog-redis     redis:7            Up 2 minutes        0.0.0.0:6379->6379/tcp
# fitlog-worker    fitlog:latest      Up 2 minutes        (no ports)
```

### 4. Verify Health

```bash
# API health check
curl http://127.0.0.1:8000/
# {"status": "ok", "service": "FitLog API", ...}

# Database health
docker compose exec postgres pg_isready -U fitlog
# accepting connections

# Redis health
docker compose exec redis redis-cli ping
# PONG

# View logs
docker compose logs -f api      # Follow API logs
docker compose logs -f worker   # Follow worker logs
docker compose logs redis       # View Redis startup
```

### 5. Initialize Database

```bash
# Run migrations (if using Alembic)
docker compose exec api uv run alembic upgrade head

# Seed sample data
docker compose exec api uv run python scripts/seed.py
```

### 6. Access Applications

```
🌐 API                 → http://127.0.0.1:8000
📚 API Documentation   → http://127.0.0.1:8000/docs
🎨 ReDoc              → http://127.0.0.1:8000/redoc
🏠 Streamlit Frontend → http://127.0.0.1:8501
```

### 7. Run Tests

```bash
# Run all tests in container
docker compose exec api uv run pytest tests/ -v

# Run specific test file
docker compose exec api uv run pytest tests/test_analytics.py -v

# Run with coverage
docker compose exec api uv run pytest tests/ --cov=app
```

### 8. Run Demo

```bash
# Interactive demo
docker compose exec api uv run python scripts/demo.py

# Async refresh script
docker compose exec api uv run python scripts/refresh.py --all
```

---

## Common Tasks

### View Application Logs

```bash
# Last 50 lines of API logs
docker compose logs api --tail 50

# Follow logs in real-time
docker compose logs -f api

# Filter logs by service
docker compose logs worker | grep "ERROR"
```

### Access Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U fitlog -d fitlog

# Common queries
\dt                          # List tables
SELECT COUNT(*) FROM user_profiles;
SELECT * FROM workout_logs;
```

### Access Redis

```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Common commands
KEYS *                       # List all keys
GET workout_summary:uuid123  # Get cached value
SETEX key 3600 value         # Set with TTL
```

### Rebuild Images

```bash
# Rebuild after code changes
docker compose build

# Rebuild and restart
docker compose up -d --build

# Force rebuild (ignore cache)
docker compose build --no-cache
```

### Scale Services

```bash
# Run multiple workers for concurrency
docker compose up -d --scale worker=3

# Check scaled services
docker compose ps
```

### Pause/Resume Services

```bash
# Pause all services (keeps state)
docker compose pause

# Resume services
docker compose unpause

# Stop services (clean shutdown)
docker compose stop

# Start services again
docker compose start
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
docker compose logs postgres
docker compose logs api
docker compose logs worker

# Restart specific service
docker compose restart api

# Rebuild if code changed
docker compose up -d --build
```

### Database Connection Error

```bash
# Check PostgreSQL is healthy
docker compose exec postgres pg_isready -U fitlog

# Check connection string in .env
echo $DATABASE_URL

# Verify port availability
netstat -an | grep 5432

# If port in use, change in compose.yaml and restart
docker compose down
docker compose up -d
```

### Redis Connection Error

```bash
# Verify Redis is running
docker compose exec redis redis-cli ping

# Check Redis logs
docker compose logs redis

# Clear Redis data
docker compose exec redis redis-cli FLUSHALL
```

### Worker Not Processing Tasks

```bash
# Check worker logs
docker compose logs -f worker

# Verify Redis broker connection
docker compose exec worker uv run python -c "from app.tasks import celery_app; print(celery_app.connection())"

# Restart worker
docker compose restart worker
```

### API Slow/Timing Out

```bash
# Check resource usage
docker stats

# Check database query performance
docker compose exec postgres psql -U fitlog -d fitlog -c "EXPLAIN ANALYZE SELECT * FROM workout_logs LIMIT 1;"

# Scale API (can't do in compose, use load balancer in production)
```

---

## Performance Optimization

### Database Indexing

```sql
-- Run in PostgreSQL
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_workout_logs_owner_id ON workout_logs(owner_id);
CREATE INDEX idx_workout_logs_log_date ON workout_logs(log_date);
CREATE INDEX idx_macro_entries_owner_id ON macro_entries(owner_id);
```

### Redis Optimization

```bash
# Monitor Redis memory
docker compose exec redis redis-cli INFO memory

# Set eviction policy
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Connection Pooling

```python
# In app/database.py
# Already configured with pool_size and max_overflow
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
)
```

---

## Security Best Practices

### Environment Variables

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use secrets manager in production
# AWS Secrets Manager, Vault, etc.
```

### Database Security

```bash
# Change default password in compose.yaml
# postgres:
#   environment:
#     POSTGRES_PASSWORD: $(openssl rand -base64 32)

# Use SSL for connections
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

### API Security

```python
# Enable CSRF protection
# Use HTTPS in production
# Implement rate limiting
# Add authentication headers
```

---

## Cleanup

```bash
# Stop all services
docker compose down

# Remove volumes (WARNING: deletes data)
docker compose down -v

# Remove everything including unused images
docker compose down -v --remove-orphans
docker prune -a
```

---

## Load Testing

```bash
# Install locust
pip install locust

# Create loadtest file
# locustfile.py with tasks for endpoints

# Run load test
locust -f locustfile.py --host=http://127.0.0.1:8000
```

---

## Monitoring & Observability

### Logs Aggregation

```bash
# Export logs
docker compose logs > logs.txt

# Parse logs for errors
docker compose logs | grep ERROR
```

### Health Check Endpoints

```bash
# Monitor in script
while true; do
  curl http://127.0.0.1:8000/ && echo "✅ API OK"
  docker compose exec postgres pg_isready -q && echo "✅ DB OK"
  docker compose exec redis redis-cli ping -q && echo "✅ Redis OK"
  sleep 30
done
```

### Metrics Collection

```python
# Use Prometheus client
# from prometheus_client import Counter, Histogram

# Track request metrics
request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

---

## Production Deployment

For production deployment, add:

1. **Load Balancer**: Nginx, Traefik
2. **TLS Certificates**: Let's Encrypt
3. **Secrets Manager**: AWS Secrets, Vault
4. **Monitoring**: Prometheus + Grafana
5. **Log Aggregation**: ELK Stack, Datadog
6. **Backup Strategy**: Automated PostgreSQL backups
7. **High Availability**: Multiple replicas, failover

---

**Last Updated: March 25, 2026**

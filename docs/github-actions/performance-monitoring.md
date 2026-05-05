# Performance Monitoring

This document describes the performance monitoring workflow for the React Login Application.

## 🎯 Purpose

The performance monitoring workflow ensures that:
- Application performance meets standards
- Performance regressions are detected early
- Bundle sizes remain optimized
- Database performance is tracked

## 🔄 Workflow Triggers

- **Push to main**: Performance baseline updates
- **Pull requests**: Performance regression detection
- **Schedule**: Daily performance monitoring

## 📋 Performance Checks

### Application Performance Tests

#### 1. Load Testing with Apache Bench
```yaml
- name: Run backend performance tests
  run: |
    # Install Apache Bench
    sudo apt-get update
    sudo apt-get install -y apache2-utils
    
    # Test login endpoint performance
    ab -n 100 -c 10 -p test_payload.json -T application/json http://localhost:5000/login || true
```

**Purpose**: Load testing for API endpoints
**Configuration**: 100 requests, 10 concurrent connections
**Metrics**: Response time, throughput, error rate

#### 2. Lighthouse CI
```yaml
- name: Run Lighthouse CI
  uses: treosh/lighthouse-ci-action@v10
  with:
    configPath: '.lighthouserc.json'
    uploadArtifacts: true
    temporaryPublicStorage: true
```

**Purpose**: Web performance auditing
**Configuration**: Defined in `.lighthouserc.json`
**Metrics**: Performance, accessibility, best practices, SEO

### Bundle Size Monitoring

#### 1. Bundle Size Analysis
```yaml
- name: Analyze bundle size
  uses: preactjs/compressed-size-action@v2
  with:
    repo-token: "${{ secrets.GITHUB_TOKEN }}"
    pattern: "./frontend/build/static/js/*.js"
```

**Purpose**: Monitor JavaScript bundle sizes
**Configuration**: Analyzes built JavaScript files
**Metrics**: Compressed and uncompressed sizes

#### 2. Bundle Size Validation
```yaml
- name: Check bundle size limits
  run: |
    cd frontend
    # Set your bundle size limits here
    MAX_MAIN_BUNDLE_SIZE=250000  # 250KB
    MAX_VENDOR_BUNDLE_SIZE=500000  # 500KB
    
    # Check main bundle size
    MAIN_BUNDLE_SIZE=$(stat -c%s build/static/js/main.*.js 2>/dev/null || echo 0)
    if [ $MAIN_BUNDLE_SIZE -gt $MAX_MAIN_BUNDLE_SIZE ]; then
      echo "Main bundle size ($MAIN_BUNDLE_SIZE bytes) exceeds limit ($MAX_MAIN_BUNDLE_SIZE bytes)"
      exit 1
    fi
```

**Purpose**: Enforce bundle size limits
**Configuration**: Customizable size limits
**Failure**: Blocks PR if limits exceeded

### Database Performance

#### 1. Database Benchmarking
```yaml
- name: Run database performance tests
  run: |
    cd backend
    python -m pytest testes/ --benchmark-only --benchmark-json=benchmark-results.json || true
```

**Purpose**: Database operation performance testing
**Tool**: pytest-benchmark
**Metrics**: Query execution times, throughput

#### 2. Benchmark Reporting
```yaml
- name: Comment PR with benchmark results
  uses: actions/github-script@v6
  if: github.event_name == 'pull_request'
  with:
    script: |
      const fs = require('fs');
      try {
        const benchmarkData = JSON.parse(fs.readFileSync('backend/benchmark-results.json', 'utf8'));
        const comment = `## Performance Benchmark Results
        
        Database operations performance:
        ${Object.entries(benchmarkData.benchmarks || {}).map(([name, data]) => 
          `- **${name}**: ${data.mean?.toFixed(2)}ms ± ${data.stddev?.toFixed(2)}ms`
        ).join('\n')}
        
        This comment will be updated if performance degrades.`;
        
        github.rest.issues.createComment({
          issue_number: context.issue.number,
          owner: context.repo.owner,
          repo: context.repo.repo,
          body: comment
        });
      } catch (error) {
        console.log('Could not read benchmark results:', error.message);
      }
```

**Purpose**: PR performance comparison
**Integration**: GitHub PR comments
**Metrics**: Performance change visualization

## 📊 Performance Standards

### Application Performance

| Metric | Target | Tool |
|--------|--------|------|
| Lighthouse Performance | ≥ 80 | Lighthouse CI |
| Lighthouse Accessibility | ≥ 90 | Lighthouse CI |
| API Response Time | ≤ 200ms | Apache Bench |
| Database Query Time | ≤ 100ms | pytest-benchmark |

### Bundle Size Limits

| Bundle Type | Max Size | Purpose |
|-------------|---------|---------|
| Main Bundle | 250KB | Application code |
| Vendor Bundle | 500KB | Third-party libraries |
| Total Bundle | 750KB | Combined size |

### Load Testing

| Metric | Target | Configuration |
|--------|--------|---------------|
| Requests per Second | ≥ 50 | 100 requests, 10 concurrent |
| Error Rate | 0% | Load testing |
| Response Time (95th percentile) | ≤ 500ms | Apache Bench |

## 🔧 Configuration

### Lighthouse Configuration

```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "settings": {
        "chromeFlags": "--no-sandbox --headless"
      },
      "url": [
        "http://localhost:3000",
        "http://localhost:3000/login"
      ]
    },
    "assert": {
      "assertions": {
        "categories:performance": ["warn", {"minScore": 0.8}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:best-practices": ["warn", {"minScore": 0.8}],
        "categories:seo": ["warn", {"minScore": 0.8}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### Environment Setup

#### Test Environment
- **Frontend**: React development server on port 3000
- **Backend**: Flask application on port 5000
- **Database**: SQLite for testing
- **Load Testing**: Apache Bench for API testing

## 📈 Performance Metrics

### Monitoring Dashboard

#### Real-time Metrics
- **Response Times**: API endpoint performance
- **Error Rates**: Application error tracking
- **Throughput**: Requests per second
- **Resource Usage**: CPU and memory utilization

#### Historical Trends
- **Performance Regression**: Over time comparisons
- **Bundle Size Growth**: Size tracking over releases
- **Database Performance**: Query performance trends
- **User Experience**: Lighthouse scores history

### Alerting

#### Performance Alerts
- **Response Time**: > 500ms average response time
- **Error Rate**: > 1% error rate
- **Bundle Size**: > 750KB total bundle size
- **Database Performance**: > 200ms average query time

#### Notification Channels
- **GitHub PR Comments**: Performance regression alerts
- **Slack Notifications**: Critical performance issues
- **Email Alerts**: Performance degradation reports

## 🚨 Troubleshooting

### Performance Issues

#### 1. Slow API Response
```bash
# Check application logs
docker-compose logs backend

# Monitor resource usage
docker stats

# Profile database queries
python -m cProfile -o profile.stats app.py
```

#### 2. Large Bundle Size
```bash
# Analyze bundle composition
npm run build -- --analyze

# Check for unused dependencies
npx depcheck

# Optimize imports
npx webpack-bundle-analyzer build/static/js/*.js
```

#### 3. Database Performance
```bash
# Run database benchmarks
python -m pytest testes/ --benchmark-only

# Check database queries
python -c "from database import engine; print(engine.execute('EXPLAIN QUERY PLAN SELECT * FROM users').fetchall())"
```

### Optimization Strategies

#### Frontend Optimization
1. **Code Splitting**: Dynamic imports for routes
2. **Tree Shaking**: Remove unused code
3. **Image Optimization**: Compress and optimize images
4. **Caching**: Implement browser caching

#### Backend Optimization
1. **Database Indexing**: Add indexes for queries
2. **Connection Pooling**: Optimize database connections
3. **Caching**: Implement Redis caching
4. **Query Optimization**: Optimize SQL queries

#### Database Optimization
1. **Index Strategy**: Proper indexing
2. **Query Optimization**: Efficient queries
3. **Connection Management**: Connection pooling
4. **Monitoring**: Performance monitoring

## 🔧 Local Development Setup

### Performance Testing Tools

```bash
# Install performance testing tools
npm install -g lighthouse
pip install pytest-benchmark

# Run Lighthouse locally
lighthouse http://localhost:3000 --output html --output-path ./lighthouse-report.html

# Run database benchmarks
cd backend
python -m pytest testes/ --benchmark-only

# Analyze bundle size
cd frontend
npm run build
npx webpack-bundle-analyzer build/static/js/*.js
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 50 -p test_payload.json -T application/json http://localhost:5000/login

# Run with custom headers
ab -H "Authorization: Bearer token" -n 100 -c 10 http://localhost:5000/api/endpoint
```

---

*For workflow configuration details, see the [workflow file](../../../.github/workflows/performance-monitoring.yml).*

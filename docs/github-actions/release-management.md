# Release Management

This document describes the release management workflow for the React Login Application.

## 🎯 Purpose

The release management workflow ensures that:
- Releases are created consistently
- Versioning follows semantic versioning
- Release notes are comprehensive
- Deployments are reliable and tracked

## 🔄 Workflow Triggers

- **Git tags**: Automated release on version tags (v*)
- **Manual dispatch**: On-demand release creation

## 📋 Release Process

### 1. Release Creation

#### Changelog Generation
```yaml
- name: Generate changelog
  id: changelog
  run: |
    # Get the previous tag
    PREVIOUS_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
    
    # Generate changelog
    if [ -n "$PREVIOUS_TAG" ]; then
      CHANGELOG=$(git log --pretty=format:"- %s (%h)" $PREVIOUS_TAG..HEAD)
    else
      CHANGELOG=$(git log --pretty=format:"- %s (%h)")
    fi
    
    # Save changelog to file
    echo "$CHANGELOG" > CHANGELOG.md
    echo "changelog<<EOF" >> $GITHUB_OUTPUT
    echo "$CHANGELOG" >> $GITHUB_OUTPUT
    echo "EOF" >> $GITHUB_OUTPUT
```

**Purpose**: Automatic changelog generation from git commits
**Method**: Git log between previous and current tags
**Output**: Structured changelog for release notes

#### GitHub Release Creation
```yaml
- name: Create Release
  uses: softprops/action-gh-release@v1
  with:
    body: |
      ## Release ${{ github.ref_name }}
      
      ### Changes
      ${{ steps.changelog.outputs.changelog }}
      
      ### Docker Images
      - Frontend: `${{ secrets.DOCKER_USERNAME }}/react-login-frontend:${{ github.ref_name }}`
      - Backend: `${{ secrets.DOCKER_USERNAME }}/react-login-backend:${{ github.ref_name }}`
      
      ### Installation
      ```bash
      docker-compose -f docker-compose.yml up -d
      ```
    files: |
      CHANGELOG.md
      docker-compose.yml
    draft: false
    prerelease: false
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Purpose**: Create GitHub release with comprehensive information
**Contents**: Changelog, Docker image tags, installation instructions
**Files**: Includes changelog and docker-compose.yml

### 2. Docker Image Building

#### Metadata Extraction
```yaml
- name: Extract metadata
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: |
      ${{ secrets.DOCKER_USERNAME }}/react-login-frontend
      ${{ secrets.DOCKER_USERNAME }}/react-login-backend
    tags: |
      type=ref,event=tag
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=semver,pattern={{major}}
```

**Purpose**: Generate Docker image tags and labels
**Tags**: Version tags, semantic versioning tags
**Labels**: Standard Docker labels for metadata

#### Frontend Image Build
```yaml
- name: Build and push frontend image
  uses: docker/build-push-action@v5
  with:
    context: ./frontend
    file: ./frontend/Dockerfile
    push: true
    tags: |
      ${{ secrets.DOCKER_USERNAME }}/react-login-frontend:${{ github.ref_name }}
      ${{ secrets.DOCKER_USERNAME }}/react-login-frontend:latest
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Purpose**: Build and push frontend Docker image
**Tags**: Version tag and latest tag
**Caching**: GitHub Actions cache for faster builds

#### Backend Image Build
```yaml
- name: Build and push backend image
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    file: ./backend/Dockerfile
    push: true
    tags: |
      ${{ secrets.DOCKER_USERNAME }}/react-login-backend:${{ github.ref_name }}
      ${{ secrets.DOCKER_USERNAME }}/react-login-backend:latest
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Purpose**: Build and push backend Docker image
**Tags**: Version tag and latest tag
**Caching**: GitHub Actions cache for faster builds

### 3. Production Deployment

#### Deployment Process
```yaml
- name: Deploy to production
  run: |
    echo "Deploying version ${{ github.ref_name }} to production..."
    # Add your production deployment commands here
    # For example:
    # docker-compose -f docker-compose.prod.yml pull
    # docker-compose -f docker-compose.prod.yml up -d
```

**Purpose**: Deploy to production environment
**Commands**: Custom deployment commands for your infrastructure
**Version**: Uses the current release version

#### Smoke Testing
```yaml
- name: Run smoke tests
  run: |
    echo "Running production smoke tests..."
    # Add smoke test commands here
```

**Purpose**: Validate production deployment
**Tests**: Basic functionality and connectivity tests

#### Deployment Notification
```yaml
- name: Notify release
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: '#releases'
    text: |
      🚀 Release ${{ github.ref_name }} deployed to production!
      Docker images: ${{ secrets.DOCKER_USERNAME }}/react-login-frontend:${{ github.ref_name }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

**Purpose**: Notify team of deployment status
**Channel**: Slack releases channel
**Content**: Release version and Docker image information

## 📊 Version Management

### Semantic Versioning

Releases follow semantic versioning (SemVer):
- **Major**: Breaking changes (2.0.0)
- **Minor**: New features (1.1.0)
- **Patch**: Bug fixes (1.0.1)

### Version Tags

Git tags should follow this format:
- `v1.0.0` - Release version
- `v1.0.0-rc.1` - Release candidate
- `v1.0.0-beta.1` - Beta release

### Branch Strategy

```
main
├── develop (development branch)
├── feature/* (feature branches)
├── release/* (release branches)
└── hotfix/* (hotfix branches)
```

## 🔧 Configuration

### Required Secrets

| Secret | Purpose | Required For |
|--------|---------|--------------|
| `DOCKER_USERNAME` | Docker Hub username | Image building |
| `DOCKER_PASSWORD` | Docker Hub password | Image building |
| `SLACK_WEBHOOK` | Slack notifications | Deployment notifications |
| `GITHUB_TOKEN` | GitHub API access | Release creation |

### Environment Configuration

#### Production Environment
- **Environment**: `production`
- **Protection**: Protected branches and environments
- **Approval**: Required for production deployments

#### Staging Environment
- **Environment**: `staging`
- **Purpose**: Pre-production testing
- **Validation**: Full testing before production

## 📈 Release Process

### Pre-Release Checklist

1. **Code Quality**
   - [ ] All tests passing
   - [ ] Code quality checks passing
   - [ ] Security scans clean
   - [ ] Performance tests passing

2. **Documentation**
   - [ ] Release notes updated
   - [ ] API documentation current
   - [ ] Installation instructions updated
   - [ ] Migration guides prepared

3. **Testing**
   - [ ] Unit tests passing
   - [ ] Integration tests passing
   - [ ] End-to-end tests passing
   - [ ] Performance tests passing

### Release Steps

1. **Tag Release**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Automated Process**
   - Changelog generation
   - GitHub release creation
   - Docker image building
   - Production deployment

3. **Post-Release**
   - Verification testing
   - Monitoring setup
   - User notification

### Rollback Process

1. **Identify Issue**
   - Monitor deployment health
   - Check error rates
   - Review user feedback

2. **Rollback Steps**
   ```bash
   # Rollback to previous version
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Communication**
   - Notify team of rollback
   - Update issue tracker
   - Communicate with users

## 📊 Release Metrics

### Release Quality

| Metric | Target | Measurement |
|--------|--------|-------------|
| Release Success Rate | 100% | Deployment success |
| Rollback Rate | < 5% | Rollback frequency |
| Time to Deploy | < 30 minutes | Deployment duration |
| Post-Release Issues | < 2 | Critical issues |

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment Time | < 30 minutes | End-to-end deployment |
| Rollback Time | < 10 minutes | Rollback duration |
| Uptime | 99.9% | Service availability |
| Response Time | < 200ms | Application performance |

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Dockerfile syntax
   - Verify build context
   - Review build logs

2. **Deployment Failures**
   - Check environment configuration
   - Verify service connectivity
   - Review deployment logs

3. **Rollback Issues**
   - Verify previous version availability
   - Check database compatibility
   - Test rollback procedures

### Debugging Steps

1. **Check Logs**
   ```bash
   docker-compose logs
   kubectl logs deployment/app
   ```

2. **Verify Services**
   ```bash
   docker-compose ps
   kubectl get pods
   ```

3. **Test Connectivity**
   ```bash
   curl http://localhost:3000/health
   curl http://localhost:5000/health
   ```

## 📚 Best Practices

### Release Management

1. **Consistent Versioning**: Follow semantic versioning
2. **Comprehensive Testing**: Test thoroughly before release
3. **Automated Processes**: Automate as much as possible
4. **Rollback Planning**: Always have rollback procedures

### Communication

1. **Release Notes**: Detailed change documentation
2. **Team Notifications**: Keep team informed
3. **User Communication**: Notify users of changes
4. **Documentation Updates**: Keep documentation current

### Security

1. **Vulnerability Scanning**: Scan before release
2. **Dependency Updates**: Keep dependencies current
3. **Access Control**: Limit release permissions
4. **Audit Logging**: Track all release activities

---

*For workflow configuration details, see the [workflow file](../../../.github/workflows/release-management.yml).*

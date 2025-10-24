# 🏷️ Version Management & Release Process

This guide explains how to manage versions and releases for TicketBroker.

## 📋 Version Strategy

### Semantic Versioning (SemVer)
We use **Semantic Versioning** format: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0): Breaking changes, incompatible API changes
- **MINOR** (1.1.0): New features, backward compatible
- **PATCH** (1.0.1): Bug fixes, backward compatible

### Examples
- `v1.0.0` - Initial release
- `v1.1.0` - Added new features
- `v1.1.1` - Bug fixes
- `v2.0.0` - Breaking changes

## 🚀 Release Process

### 1. Development Workflow
```bash
# Work on features/bugs
git checkout -b feature/new-feature
# ... make changes ...
git commit -m "Add new feature"
git push origin feature/new-feature

# Create Pull Request
# ... review and merge ...
```

### 2. Create Release
```bash
# Switch to main branch
git checkout main
git pull origin main

# Create and push tag
git tag v1.2.3
git push origin v1.2.3
```

### 3. Automated Build
- ✅ **GitHub Actions** automatically builds Docker image
- ✅ **Creates GitHub Release** with download links
- ✅ **Publishes to Container Registry** with multiple tags

## 🐳 Docker Image Tags

### Tag Strategy
When you push `v1.2.3`, GitHub Actions creates these tags:

```bash
ghcr.io/magpern/ticketbroker:v1.2.3    # Exact version
ghcr.io/magpern/ticketbroker:v1.2       # Minor version
ghcr.io/magpern/ticketbroker:v1         # Major version
ghcr.io/magpern/ticketbroker:latest     # Latest stable
```

### Version Selection
```bash
# Deploy specific version
./deploy-pi.sh v1.2.3

# Deploy latest stable
./deploy-pi.sh latest

# Deploy minor version (gets latest patch)
./deploy-pi.sh v1.2
```

## 📦 Deployment Examples

### Raspberry Pi Deployment
```bash
# Deploy specific version
./deploy-pi.sh v1.2.3

# Deploy latest
./deploy-pi.sh latest

# Check what's running
docker-compose -f docker-compose.pi.yml ps
```

### Manual Docker Commands
```bash
# Pull specific version
docker pull ghcr.io/magpern/ticketbroker:v1.2.3

# Run specific version
docker run -d \
  --name ticketbroker \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret \
  ghcr.io/magpern/ticketbroker:v1.2.3
```

## 🔄 Rollback Strategy

### Quick Rollback
```bash
# Rollback to previous version
./deploy-pi.sh v1.1.0

# Check available versions
docker images ghcr.io/magpern/ticketbroker
```

### Emergency Rollback
```bash
# Stop current container
docker-compose -f docker-compose.pi.yml down

# Start previous version
docker run -d \
  --name ticketbroker-emergency \
  -p 5000:5000 \
  -v ./data:/data \
  ghcr.io/magpern/ticketbroker:v1.1.0
```

## 📊 Version Tracking

### Check Current Version
```bash
# Check running container version
docker inspect ticketbroker-ticketbroker-1 | grep Image

# Check available versions
docker images ghcr.io/magpern/ticketbroker --format "table {{.Tag}}\t{{.CreatedAt}}"
```

### Version History
```bash
# View all tags in repository
git tag --sort=-version:refname

# View release notes
gh release list
```

## 🛠️ Development vs Production

### Development
- ✅ **Push to feature branches** - no builds
- ✅ **Test locally** with `docker-compose up`
- ✅ **Create PR** for review

### Production
- ✅ **Tag releases** - triggers builds
- ✅ **Deploy to Raspberry Pi** with specific versions
- ✅ **Monitor health** and logs

## 🔐 Security Considerations

### Version Pinning
```yaml
# Always pin specific versions in production
image: ghcr.io/magpern/ticketbroker:v1.2.3  # ✅ Specific version
image: ghcr.io/magpern/ticketbroker:latest  # ⚠️ Use with caution
```

### Environment Variables
```bash
# Use different configs for different environments
# .env.production
SECRET_KEY=production-secret-key
ADMIN_PASSWORD=secure-production-password

# .env.staging  
SECRET_KEY=staging-secret-key
ADMIN_PASSWORD=staging-admin-password
```

## 📈 Benefits

✅ **Controlled Releases** - Only build when ready  
✅ **Version Tracking** - Clear version history  
✅ **Rollback Capability** - Easy to revert changes  
✅ **Resource Efficiency** - No unnecessary builds  
✅ **Release Management** - Automated GitHub releases  
✅ **Multi-Environment** - Different versions for different environments  

## 🎯 Best Practices

1. **Always tag releases** - Don't deploy untagged code
2. **Use semantic versioning** - Clear version progression
3. **Pin versions in production** - Avoid surprise updates
4. **Test before tagging** - Ensure quality before release
5. **Document changes** - Use GitHub releases for changelog
6. **Monitor deployments** - Check health after deployment

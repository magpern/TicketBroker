# 🚀 Automated Docker Deployment for Raspberry Pi

This guide explains how to set up automated Docker builds on GitHub and deploy them to your Raspberry Pi.

## 📋 Prerequisites

### GitHub Repository Setup
1. **Push your code** to GitHub
2. **Enable GitHub Container Registry** (ghcr.io)
3. **Set up GitHub Actions** (automatically enabled)

### Raspberry Pi Setup
1. **Install Docker** on Raspberry Pi:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Install Docker Compose**:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose-plugin
   ```

## 🔧 Configuration Steps

### 1. Update GitHub Actions Workflow

Edit `.github/workflows/docker-build.yml` and replace:
```yaml
IMAGE_NAME: ${{ github.repository }}
```
with your actual repository name.

### 2. Update Raspberry Pi Configuration

Edit `docker-compose.pi.yml` and replace:
```yaml
image: ghcr.io/YOUR_USERNAME/ticketbroker:latest
```
with your actual GitHub username and repository name.

### 3. Set Up Environment Variables

On your Raspberry Pi, create a `.env` file:
```bash
# .env file for Raspberry Pi
SECRET_KEY=your-production-secret-key
MAIL_PASSWORD=your-gmail-app-password
ADMIN_PASSWORD=your-secure-admin-password
```

## 🚀 Deployment Process

### Automatic Build (GitHub Actions)
1. **Push code** to master/main branch
2. **GitHub Actions** automatically:
   - Builds Docker image for AMD64 and ARM64
   - Pushes to GitHub Container Registry
   - Tags with branch name and commit SHA

### Manual Deployment (Raspberry Pi)
1. **SSH into your Raspberry Pi**
2. **Run deployment script**:
   ```bash
   ./deploy-pi.sh
   ```

### Alternative: Direct Docker Compose
```bash
# Pull latest image
docker pull ghcr.io/YOUR_USERNAME/ticketbroker:latest

# Start/update container
docker-compose -f docker-compose.pi.yml up -d
```

## 🔍 Monitoring

### Check Container Status
```bash
docker-compose -f docker-compose.pi.yml ps
```

### View Logs
```bash
docker-compose -f docker-compose.pi.yml logs -f
```

### Health Check
```bash
curl http://localhost:5000/
```

## 🛠️ Troubleshooting

### Image Not Found
- Check GitHub Container Registry permissions
- Verify image name and tag

### ARM64 Build Issues
- GitHub Actions automatically builds for ARM64
- Use `docker buildx` for local ARM64 builds

### Permission Issues
- Ensure Docker group membership: `sudo usermod -aG docker $USER`
- Log out and back in after adding to Docker group

## 📊 Architecture Support

The GitHub Actions workflow builds for:
- **AMD64** (Intel/AMD processors)
- **ARM64** (Raspberry Pi 4, Apple M1/M2)

## 🔐 Security Notes

- **Container Registry** requires authentication
- **Environment variables** should be set securely
- **Database** is persisted in `./data` volume
- **Images** are automatically scanned for vulnerabilities

## 📈 Benefits

✅ **Automated builds** on every push  
✅ **Multi-architecture** support  
✅ **Easy deployment** to Raspberry Pi  
✅ **Version control** with Git tags  
✅ **Security scanning** built-in  
✅ **Rollback capability** with image tags  

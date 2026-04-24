# Deployment Guide - Network Attack Detection System

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Configuration](#production-configuration)

---

## Local Development

### Prerequisites
- Python 3.10+
- MySQL 8.0+ (optional, fallback to demo mode)
- Redis 6.0+ (optional, for caching)
- 4GB RAM minimum

### Installation
```bash
# Clone repository
git clone <repository-url>
cd "Network attack dectection system"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database (optional)
python database/db_setup.py

# Run application
python app.py
```

### Access Application
- Dashboard: `http://localhost:5000`
- API: `http://localhost:5000/api/*`

---

## Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Quick Start
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f nads

# Stop services
docker-compose down
```

### Access Services
- NADS Dashboard: `http://localhost:5000`
- MySQL: `localhost:3306`
- Redis: `localhost:6379`
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`

### Scaling
```bash
# Scale specific services
docker-compose up -d --scale nads=3

# Load balance with Nginx (configure separately)
```

### Custom Configuration
```bash
# Override environment variables
docker-compose -f docker-compose.yml \
  -e MYSQL_PASSWORD=custom_password \
  up -d
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes 1.20+
- kubectl CLI
- Container registry (Docker Hub, ECR, GCR, etc.)

### Create Kubernetes Resources
```bash
# Create namespace
kubectl create namespace nads

# Create ConfigMap for configuration
kubectl create configmap nads-config \
  --from-file=config.py \
  -n nads

# Create Secret for sensitive data
kubectl create secret generic nads-secrets \
  --from-literal=mysql-password=secure-password \
  --from-literal=api-key=api-key-here \
  -n nads
```

### Deploy Application
```yaml
# nads-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nads
  namespace: nads
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nads
  template:
    metadata:
      labels:
        app: nads
    spec:
      containers:
      - name: nads
        image: <registry>/nads:latest
        ports:
        - containerPort: 5000
        env:
        - name: MYSQL_HOST
          value: mysql-service
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: nads-secrets
              key: mysql-password
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Deploy to Kubernetes
```bash
# Apply deployment
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/mysql.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get all -n nads

# Port forward for testing
kubectl port-forward -n nads svc/nads 5000:5000

# Scale deployment
kubectl scale deployment nads -n nads --replicas=5

# Rolling update
kubectl set image deployment/nads \
  nads=<registry>/nads:v2 -n nads
```

### Monitoring
```bash
# Check pod logs
kubectl logs -f deployment/nads -n nads

# Monitor metrics
kubectl top pods -n nads

# Describe resources
kubectl describe pod <pod-name> -n nads
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2
```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --region us-east-1

# SSH and install
ssh -i key.pem ec2-user@<instance-ip>
# Then follow local development installation
```

#### Using ECS
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name nads

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster nads \
  --service-name nads \
  --task-definition nads \
  --desired-count 3
```

#### Using RDS for MySQL
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier nads-mysql \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password <password>

# Update app configuration
export MYSQL_HOST=<rds-endpoint>
```

### Azure Deployment

#### Using Azure Container Instances
```bash
# Create resource group
az group create --name nads-rg --location eastus

# Create container instance
az container create \
  --resource-group nads-rg \
  --name nads \
  --image <registry>/nads:latest \
  --cpu 2 --memory 1 \
  --ports 5000 \
  --environment-variables MYSQL_HOST=<host>
```

#### Using Azure Kubernetes Service (AKS)
```bash
# Create cluster
az aks create \
  --resource-group nads-rg \
  --name nads-cluster \
  --node-count 3

# Get credentials
az aks get-credentials \
  --resource-group nads-rg \
  --name nads-cluster

# Deploy (same as Kubernetes section)
```

### Google Cloud Deployment

#### Using Cloud Run
```bash
# Build and push image
gcloud builds submit \
  --tag gcr.io/<project>/nads \
  .

# Deploy to Cloud Run
gcloud run deploy nads \
  --image gcr.io/<project>/nads \
  --platform managed \
  --memory 1024Mi \
  --set-env-vars MYSQL_HOST=<cloudsql-ip>
```

#### Using Google Kubernetes Engine (GKE)
```bash
# Create cluster
gcloud container clusters create nads \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --zone us-central1-a

# Deploy (same as Kubernetes section)
```

---

## Production Configuration

### Environment Variables
```bash
# .env.production
FLASK_ENV=production
DEBUG=False

# Database
MYSQL_HOST=prod-mysql.example.com
MYSQL_USER=nads_user
MYSQL_PASSWORD=<secure-password>
MYSQL_DATABASE=network_security

# Redis
REDIS_HOST=prod-redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=<secure-password>

# Security
SECRET_KEY=<generate-with-secrets.token_hex(32)>
JWT_SECRET_KEY=<generate-with-secrets.token_hex(32)>

# Logging
LOG_LEVEL=INFO
LOG_DIR=/var/log/nads

# Features
AUTO_RESPONSE_ENABLED=true
NETWORK_CAPTURE_ENABLED=true
ML_MODEL_ENABLED=true
```

### Security Hardening
```bash
# Set restrictive file permissions
chmod 600 .env
chmod 755 /app

# Use strong passwords
openssl rand -base64 32  # Generate secure password

# Enable HTTPS
# Configure reverse proxy (Nginx/Apache) with SSL certificates

# Restrict network access
# Configure firewall rules
# Whitelist only necessary ports (5000, 443, 3306)

# Enable audit logging
# Configure ELK stack for centralized logging
```

### Performance Tuning
```bash
# MySQL tuning
max_connections=1000
innodb_buffer_pool_size=2G

# Redis configuration
maxmemory=512mb
maxmemory-policy=allkeys-lru

# Flask configuration
WORKERS=4  # For production server
THREADS=2
WORKER_CLASS=sync
```

### Monitoring & Alerting
```bash
# Install monitoring agents
# Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# ELK Stack for logs
docker-compose -f docker-compose.elk.yml up -d

# Configure alerts
# Health check: /api/health
# Alert on response time > 1s
# Alert on error rate > 5%
```

### Backup & Recovery
```bash
# Database backup
mysqldump -u admin -p database_name > backup.sql

# Automated backups
0 2 * * * /usr/bin/mysqldump -u admin -p db > /backups/db_$(date +\%Y\%m\%d).sql

# Restore
mysql -u admin -p database_name < backup.sql
```

### High Availability
```bash
# MySQL Master-Slave replication
# Redis Sentinel for failover
# Load balancer (HAProxy/Nginx)
# Multiple NADS instances
```

---

## Troubleshooting

### Common Issues

#### MySQL Connection Error
```bash
# Check MySQL is running
docker ps | grep mysql

# Verify credentials
mysql -h localhost -u nads_user -p

# Check network connectivity
telnet mysql 3306
```

#### Redis Connection Error
```bash
# Check Redis is running
docker ps | grep redis

# Verify connection
redis-cli ping

# Check for port conflicts
lsof -i :6379
```

#### WebSocket Connection Issues
```bash
# Ensure flask-socketio is installed
pip install flask-socketio python-socketio

# Check browser console for errors
# Verify CORS settings
# Check firewall rules for WebSocket (typically port 443 or same as HTTP)
```

### Logs
```bash
# Docker logs
docker-compose logs -f nads

# Application logs
tail -f logs/app.log

# Database logs
docker-compose logs -f mysql

# System logs
journalctl -u nads -f
```

---

## Maintenance

### Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose pull
docker-compose up -d

# Update Kubernetes deployments
kubectl rollout restart deployment/nads -n nads
```

### Health Checks
```bash
# Check system health
curl http://localhost:5000/api/health

# Monitor logs
tail -f logs/app.log

# Database integrity
mysql> CHECK TABLE incidents, network_packets, threats;
```

### Cleanup
```bash
# Remove old logs
find logs -mtime +30 -delete

# Prune Docker images
docker image prune -a

# Database maintenance
mysql> OPTIMIZE TABLE incidents;
```

---

## Support
For issues or questions, refer to:
- README.md - Project overview
- API_DOCUMENTATION.md - API reference
- IMPLEMENTATION_SUMMARY.md - Architecture details

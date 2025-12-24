# Deployment Guide

This guide covers deploying the AI Interviewer Platform to production.

## Quick Start - Cheapest Options

**Fastest & Free**: [Fly.io](#option-1-flyio-free---recommended-for-cheapest) - Free tier, ~5 min setup  
**Easiest**: [Railway](#option-2-railway-5month---easiest) - $5/month, auto-deploys from GitHub  
**Cheapest VPS**: [Hetzner](#option-3-hetzner-vps-4month---full-control) - ~$4/month, full control

## Prerequisites

- Docker and Docker Compose installed
- Account on a hosting platform (Railway, Render, Fly.io, etc.)
- OpenAI API key
- OpenRouter API key

## Environment Variables

### Required Variables

- `OPENAI_API_KEY` - OpenAI API key for Whisper transcription service
- `OPENROUTER_API_KEY` - OpenRouter API key for DSPy LLM access

### Optional Variables

- `OPENROUTER_MODEL` - LLM model identifier (default: "openai/gpt-4o-mini")
- `OPENAI_MODEL` - Whisper model (default: "whisper-1")
- `MAX_AUDIO_SIZE_MB` - Maximum audio file size in MB (default: 25)
- `API_BASE_URL` - Backend API URL (default: "http://localhost:8000")
- `CORS_ORIGINS` - Comma-separated list of allowed origins (default: "http://localhost:8501")
- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: "INFO")
- `DEBUG_MODE` - Enable debug mode (default: "false")
- `DATABASE_PATH` - SQLite database file path (default: "data/interviews.db")
- `API_TIMEOUT` - HTTP request timeout in seconds (default: 10.0)

## Local Testing with Docker Compose

1. **Create `.env` file**:
   ```bash
   cp .env.example .env
   # Edit .env and fill in your API keys
   ```

2. **Build and start services**:
   ```bash
   docker compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/health

4. **Stop services**:
   ```bash
   docker compose down
   ```

## Production Deployment - Cheap Options

### Option 1: Fly.io (FREE - Recommended for cheapest)

**Cost**: Free tier includes 3 shared VMs, 160GB outbound data/month

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Initialize app** (uses existing `fly.toml`):
   ```bash
   fly launch --no-deploy
   ```
   - When prompted, choose a region close to you (e.g., `iad` for US East)
   - Don't deploy yet

4. **Create volume for database**:
   ```bash
   fly volumes create data --size 1 --region iad
   ```
   (Replace `iad` with your chosen region)

5. **Set secrets** (replace with your actual values):
   ```bash
   fly secrets set OPENAI_API_KEY=sk-your-openai-key
   fly secrets set OPENROUTER_API_KEY=sk-or-your-openrouter-key
   fly secrets set CORS_ORIGINS=https://ai-interviewer-platform.fly.dev
   fly secrets set API_BASE_URL=http://localhost:8000
   ```
   Note: `API_BASE_URL` uses `localhost:8000` because both services run in the same container. The frontend will proxy API calls internally.

6. **Deploy**:
   ```bash
   fly deploy
   ```

7. **Open your app**:
   ```bash
   fly open
   ```

**Note**: Your app URL will be `https://ai-interviewer-platform.fly.dev` (or whatever name you chose). The backend is accessible on port 8000, but Fly.io routes HTTP traffic to port 8501 (frontend) by default. You may need to configure a second app for the backend API, or use the same app with different ports.

**For single-app deployment** (both services in one):
- The `start.sh` script runs both services
- Frontend is on port 8501 (exposed via HTTP)
- Backend is on port 8000 (internal only, or configure separate app)

**Monitor**:
```bash
fly logs
fly status
```

---

### Option 2: Railway ($5/month - Easiest)

**Cost**: $5/month for hobby plan (includes $5 credit)

1. **Sign up** at [railway.app](https://railway.app)

2. **Create new project** → "Deploy from GitHub repo"

3. **Select your repository**

4. **Add environment variables** in Railway dashboard:
   - `OPENAI_API_KEY` = your OpenAI key
   - `OPENROUTER_API_KEY` = your OpenRouter key
   - `CORS_ORIGINS` = `https://your-app.up.railway.app`
   - `API_BASE_URL` = `https://your-app.up.railway.app:8000`
   - `DATABASE_PATH` = `data/interviews.db`

5. **Configure deployment**:
   - Railway auto-detects Dockerfile
   - Set root directory to `/` (default)
   - Build command: (auto-detected)
   - Start command: `/app/scripts/start.sh`

6. **Add volume** for database persistence:
   - Go to your service → "Volumes" tab
   - Add volume: mount `/app/data` (this persists your SQLite DB)

7. **Deploy**: Railway auto-deploys on git push

**Note**: Railway exposes port 8501 by default. You may need to configure both ports (8000 and 8501) or use a single port with a reverse proxy.

---

### Option 3: Hetzner VPS (~$4/month - Full Control)

**Cost**: ~€4/month (~$4.30) for CX11 VPS

1. **Sign up** at [hetzner.com](https://www.hetzner.com/cloud)

2. **Create VPS**:
   - Location: Choose closest to you
   - Image: Ubuntu 22.04
   - Type: CX11 (1 vCPU, 2GB RAM) - €4.15/month

3. **SSH into server**:
   ```bash
   ssh root@your-server-ip
   ```

4. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

5. **Clone your repo**:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

6. **Create `.env` file**:
   ```bash
   nano .env
   ```
   Add:
   ```
   OPENAI_API_KEY=sk-your-key
   OPENROUTER_API_KEY=sk-or-your-key
   CORS_ORIGINS=https://your-domain.com
   API_BASE_URL=https://your-domain.com:8000
   DATABASE_PATH=data/interviews.db
   ```

7. **Deploy with Docker Compose**:
   ```bash
   docker compose up -d --build
   ```

8. **Set up reverse proxy** (Nginx):
   ```bash
   apt update && apt install nginx certbot python3-certbot-nginx -y
   ```

9. **Configure Nginx** (`/etc/nginx/sites-available/default`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
       }
   }
   ```

10. **Get SSL certificate**:
    ```bash
    certbot --nginx -d your-domain.com
    ```

11. **Auto-start on reboot**:
    ```bash
    systemctl enable docker
    ```

**Monitor**:
```bash
docker compose logs -f
docker compose ps
```

---

### Option 4: Render (Free tier available, but limited)

**Cost**: Free tier available, but sleeps after inactivity. Paid starts at $7/month.

1. **Sign up** at [render.com](https://render.com)

2. **Create new Web Service** → Connect GitHub repo

3. **Configure**:
   - Build Command: `docker build -t ai-interviewer .`
   - Start Command: `/app/scripts/start.sh`
   - Environment: Docker

4. **Add environment variables** (same as Railway)

5. **Add persistent disk**:
   - Go to "Disks" → Add disk
   - Mount path: `/app/data`
   - Size: 1GB

6. **Deploy**: Auto-deploys on git push

**Note**: Free tier sleeps after 15min inactivity. Paid tier keeps it running.

### Heroku

1. **Install Heroku CLI**
2. **Create app**: `heroku create your-app-name`
3. **Set config vars**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set OPENROUTER_API_KEY=your_key
   heroku config:set CORS_ORIGINS=https://your-app.herokuapp.com
   ```
4. **Deploy**: `git push heroku main`
5. **Note**: Heroku uses ephemeral filesystem - consider using external database for production

## Monolithic Deployment

For platforms that support single-container deployments:

1. **Use the startup script** (`scripts/start.sh`) to run both services
2. **Configure environment variables** as above
3. **Set up volume mounts** for `/app/data` directory
4. **Expose ports**: 8000 (backend) and 8501 (frontend)

## Health Checks

- **Backend**: `GET /health` - Returns `{"status": "healthy"}`
- **Frontend**: Streamlit health check endpoint (if available)

## Database Persistence

The SQLite database is stored in `/app/data/interviews.db` by default. Ensure this directory is mounted as a volume or persistent storage on your hosting platform.

## CORS Configuration

For production, set `CORS_ORIGINS` to your frontend URL:
```bash
CORS_ORIGINS=https://your-frontend-domain.com
```

For multiple origins:
```bash
CORS_ORIGINS=https://app.example.com,https://staging.example.com
```

**Security Note**: Avoid using `"*"` in production unless necessary.

## Password Protection

If password protection is required:

1. **Streamlit Authentication**: Configure via `~/.streamlit/config.toml`
2. **Platform-level**: Use hosting platform's authentication features
3. **Document credentials**: If password protection is used, document credentials in secure location

## Troubleshooting

### Backend won't start
- Check environment variables are set correctly
- Verify API keys are valid
- Check logs: `docker compose logs backend`

### Frontend can't connect to backend
- Verify `API_BASE_URL` is set correctly
- Check `CORS_ORIGINS` includes frontend URL
- Ensure backend is healthy: `curl http://localhost:8000/health`

### Database errors
- Ensure `/app/data` directory has write permissions
- Check `DATABASE_PATH` is set correctly
- Verify volume mounts are configured

### Port conflicts
- Change ports in `docker-compose.yml` if needed
- Update `CORS_ORIGINS` and `API_BASE_URL` accordingly

## Monitoring

- Check application logs regularly
- Monitor health check endpoints
- Set up alerts for failed health checks
- Monitor API usage and costs

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use platform secrets management** for production
3. **Restrict CORS origins** to specific domains
4. **Set `DEBUG_MODE=false`** in production
5. **Use HTTPS** for all production deployments
6. **Regularly rotate API keys**
7. **Monitor logs** for suspicious activity

## Support

For issues or questions:
- Check application logs
- Review environment variable configuration
- Verify API keys are valid and have sufficient credits
- Check hosting platform status pages


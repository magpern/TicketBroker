# Gunicorn configuration file for production deployment
# Usage: gunicorn -c gunicorn.conf.py run:app

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/logs/access.log"
errorlog = "/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ticketbroker"

# Server mechanics
daemon = False
pidfile = "/logs/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Environment variables
raw_env = [
    'FLASK_APP=run.py',
    'FLASK_ENV=production',
]

# Preload app for better performance
preload_app = True

# Worker timeout for graceful shutdown
graceful_timeout = 30

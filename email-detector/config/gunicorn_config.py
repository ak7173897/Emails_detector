"""
Production Gunicorn Configuration
Optimized for security and performance
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeout settings
timeout = 30
keepalive = 5
graceful_timeout = 30

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8192

# Process naming
proc_name = 'email-detector'

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process management
pidfile = '/tmp/email-detector.pid'
user = None  # Set to appropriate user in production
group = None  # Set to appropriate group in production

# SSL (if terminating SSL at application level)
# keyfile = '/path/to/private.key'
# certfile = '/path/to/certificate.crt'

# Preload application
preload_app = True

# Worker recycling
max_requests = 1000
max_requests_jitter = 50

def when_ready(server):
    """Called when the server is ready to receive requests."""
    server.log.info("Email Security Detector is ready to receive requests")

def worker_int(worker):
    """Called when worker receives INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called before worker processes are forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called after worker processes are forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when worker is killed."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
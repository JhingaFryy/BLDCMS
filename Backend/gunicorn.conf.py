"""Module 45: production Gunicorn configuration - Uvicorn workers, bound to localhost only
(Nginx is the public-facing layer; see Documentation/DEPLOYMENT.md). Invoked via:

    gunicorn -c gunicorn.conf.py main:app

or indirectly via the bldcms-backend.service systemd unit, which is how this is actually run in
production - this file is not meant to be edited per-deployment; use environment variables
(already the established pattern for DATABASE_URL/JWT_SECRET_KEY/CORS_ORIGINS, see
app/database/database.py, app/security/jwt.py, main.py) for anything that varies by host.
"""
import multiprocessing
import os

# Bind to localhost only - Nginx (or another reverse proxy) is the only thing that should ever
# reach this process directly. Never expose this port to 0.0.0.0 in production.
bind = "127.0.0.1:8080"

# One worker per CPU core. Unlike Gunicorn's classic sync-worker heuristic (2 x cores + 1),
# UvicornWorker is async - each worker already handles many concurrent connections via asyncio,
# so scaling by core count (not request volume) is the standard starting point for CPU-bound
# parallelism (PDF generation, signature verification). Tune via the GUNICORN_WORKERS env var if
# load testing on the real production host shows a different number is better.
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count()))

worker_class = "uvicorn.workers.UvicornWorker"

# Recycle each worker after ~1000 requests (jittered so all workers don't recycle at once) - a
# standard defense against slow memory growth over a long-running process, cheap insurance.
max_requests = 1000
max_requests_jitter = 100

# Generous beyond FastAPI/Starlette's own defaults to comfortably cover PDF generation and
# digital-signature verification requests, which do real CPU work (pyHanko/pypdf/ReportLab)
# rather than just proxying - a request should fail with a real error before it's ever killed by
# a worker timeout under normal load.
timeout = 60
graceful_timeout = 30
keepalive = 5

# Deliberately NOT enabled. Enabling this would import the app (and therefore create
# app.database.database's module-level SQLAlchemy engine/connection pool) once in the master
# process *before* forking workers - every worker would then inherit the same underlying
# psycopg2 socket file descriptors across fork, a well-known source of corrupted/shared database
# connections. Leaving this False means each worker imports the app fresh after forking, so each
# gets its own independent engine and connection pool.
preload_app = False

# Gunicorn's own operational log (worker boot/exit, timeouts, restarts) - NOT the application's
# own structured logs, which continue to write to backend/logs/*.log exactly as before via
# app/core/logging.py, unaffected by this file. "-" means stdout/stderr, which the
# bldcms-backend.service systemd unit captures into the journal (journalctl -u bldcms-backend).
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Avoids known issues with the heartbeat/temp file gunicorn workers use on some filesystems -
# /dev/shm is tmpfs (RAM-backed) and always writable regardless of where the app is deployed.
worker_tmp_dir = "/dev/shm"

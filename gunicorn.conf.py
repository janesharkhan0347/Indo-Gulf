import os

bind    = f"0.0.0.0:{os.environ.get('PORT', '7860')}"
workers = 2
timeout = 120
worker_class = 'sync'
accesslog = '-'
errorlog  = '-'
loglevel  = 'info'
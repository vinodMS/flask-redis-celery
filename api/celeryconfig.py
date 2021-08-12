# celeryconfig.py
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/Amsterdam"
enable_utc = True
worker_pool_restarts = True
broker_pool_limit = 0

from prometheus_client import Counter, Gauge, REGISTRY

if 'command_calls_total' not in REGISTRY._names_to_collectors:
    COMMAND_COUNTER = Counter('command_calls_total', 'Total number of command calls', ['command'])
if 'errors_total' not in REGISTRY._names_to_collectors:
    ERROR_COUNTER = Counter('errors_total', 'Total number of errors')
if 'requests_total' not in REGISTRY._names_to_collectors:
    REQUEST_COUNTER = Counter('requests_total', 'Total number of requests (DB requests)')
if 'active_users' not in REGISTRY._names_to_collectors:
    ACTIVE_USERS = Gauge('active_users', 'Number of currently active users')

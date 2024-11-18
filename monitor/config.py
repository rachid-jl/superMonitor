"""Configuration settings for the system monitor."""

REFRESH_RATE = 10  # seconds
LOG_LIMIT = 10

# System thresholds
THRESHOLDS = {
    'cpu': {
        'warning': 70,
        'critical': 90
    },
    'memory': {
        'warning': 70,
        'critical': 90
    },
    'disk': {
        'warning': 80,
        'critical': 95
    }
}

# Services configuration
MONITORED_SERVICES = [
    {
        'name': 'web-server',
        'port': 80,
        'type': 'http'
    },
    {
        'name': 'database',
        'port': 5432,
        'type': 'tcp'
    },
    {
        'name': 'cache-service',
        'port': 6379,
        'type': 'tcp'
    }
]
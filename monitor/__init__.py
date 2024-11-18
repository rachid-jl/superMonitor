"""System monitor package."""
from .metrics import MetricsCollector
from .display import create_dashboard
from .config import REFRESH_RATE, MONITORED_SERVICES, THRESHOLDS

__version__ = '1.0.0'
__all__ = ['MetricsCollector', 'create_dashboard', 'REFRESH_RATE', 
           'MONITORED_SERVICES', 'THRESHOLDS']
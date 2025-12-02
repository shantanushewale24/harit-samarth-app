"""
Monitoring and Logging Utilities for Soil Health Backend
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import functools
import time

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(log_dir: str = 'logs', log_level: str = 'INFO') -> logging.Logger:
    """
    Setup logging configuration
    """
    Path(log_dir).mkdir(exist_ok=True)
    
    logger = logging.getLogger('soil_health')
    logger.setLevel(getattr(logging, log_level))
    
    # File handler - JSON format
    json_handler = logging.FileHandler(
        os.path.join(log_dir, 'app.json.log')
    )
    json_handler.setFormatter(JSONFormatter())
    logger.addHandler(json_handler)
    
    # File handler - Text format
    text_handler = logging.FileHandler(
        os.path.join(log_dir, 'app.log')
    )
    text_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    text_handler.setFormatter(text_formatter)
    logger.addHandler(text_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(text_formatter)
    logger.addHandler(console_handler)
    
    return logger


class PerformanceMonitor:
    """Monitor API performance"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger('soil_health')
        self.metrics = {
            'total_requests': 0,
            'total_errors': 0,
            'total_anomalies_detected': 0,
            'avg_response_time': 0,
            'response_times': []
        }
    
    def record_request(self, endpoint: str, response_time: float, success: bool = True):
        """Record API request metrics"""
        self.metrics['total_requests'] += 1
        self.metrics['response_times'].append(response_time)
        
        if not success:
            self.metrics['total_errors'] += 1
        
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
        
        # Update average
        self.metrics['avg_response_time'] = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        self.logger.info(
            f"Request: {endpoint} - {response_time:.2f}ms - {'Success' if success else 'Error'}"
        )
    
    def record_anomaly(self, anomaly_score: float):
        """Record anomaly detection"""
        self.metrics['total_anomalies_detected'] += 1
        self.logger.info(f"Anomaly detected with score: {anomaly_score:.3f}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            **self.metrics,
            'error_rate': (self.metrics['total_errors'] / self.metrics['total_requests'] * 100) 
                         if self.metrics['total_requests'] > 0 else 0
        }
    
    def reset_metrics(self):
        """Reset metrics"""
        self.metrics = {
            'total_requests': 0,
            'total_errors': 0,
            'total_anomalies_detected': 0,
            'avg_response_time': 0,
            'response_times': []
        }


def timing_decorator(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('soil_health')
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} executed in {elapsed:.2f}ms")
            return result
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {elapsed:.2f}ms: {str(e)}")
            raise
    return wrapper


class HealthCheckRegistry:
    """Track health check status"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger('soil_health')
        self.checks = {
            'model_loaded': False,
            'csv_accessible': False,
            'api_responding': True,
            'last_check': None
        }
    
    def update_check(self, check_name: str, status: bool, details: str = ''):
        """Update a health check"""
        if check_name in self.checks:
            self.checks[check_name] = status
            self.checks['last_check'] = datetime.now().isoformat()
            self.logger.info(f"Health check '{check_name}': {status} {details}")
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return all(v for k, v in self.checks.items() if k != 'last_check')
    
    def get_status(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            **self.checks,
            'overall': 'Healthy' if self.is_healthy() else 'Unhealthy'
        }


class AlertManager:
    """Manage system alerts"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger('soil_health')
        self.alerts = []
        self.max_alerts = 1000
    
    def create_alert(self, severity: str, message: str, details: Dict = None):
        """Create an alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'message': message,
            'details': details or {}
        }
        
        self.alerts.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        log_level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(log_level, f"[{severity.upper()}] {message}")
        
        return alert
    
    def get_alerts(self, severity: str = None, limit: int = 100) -> list:
        """Get alerts"""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        
        return alerts[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
        self.logger.info("Alerts cleared")


# Global instances
logger = setup_logging()
performance_monitor = PerformanceMonitor(logger)
health_check_registry = HealthCheckRegistry(logger)
alert_manager = AlertManager(logger)


def get_logger():
    """Get the global logger"""
    return logger

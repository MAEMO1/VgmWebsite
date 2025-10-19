"""
Structured logging configuration for VGM Website
Uses structlog for JSON output, request ID tracing, and proper log levels
"""

import structlog
import logging
import uuid
import time
from typing import Any, Dict, Optional
from flask import request, g
from datetime import datetime

def add_request_id(logger, method_name, event_dict):
    """Add request ID to log events"""
    if hasattr(g, 'request_id'):
        event_dict['request_id'] = g.request_id
    return event_dict

def add_timestamp(logger, method_name, event_dict):
    """Add ISO timestamp to log events"""
    event_dict['timestamp'] = datetime.utcnow().isoformat()
    return event_dict

def add_user_context(logger, method_name, event_dict):
    """Add user context to log events"""
    if hasattr(g, 'user_id'):
        event_dict['user_id'] = g.user_id
    if hasattr(g, 'user_role'):
        event_dict['user_role'] = g.user_role
    return event_dict

def setup_logging(environment: str = 'development'):
    """Setup structured logging configuration"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=open("logs/app.log", "a") if environment == 'production' else None,
        level=logging.INFO if environment == 'production' else logging.DEBUG,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            add_timestamp,
            add_request_id,
            add_user_context,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if environment == 'production' else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

def log_request_start():
    """Log the start of a request"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    
    logger = get_logger('request')
    logger.info(
        "Request started",
        method=request.method,
        path=request.path,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        content_type=request.content_type,
    )

def log_request_end():
    """Log the end of a request"""
    duration = time.time() - g.start_time
    
    logger = get_logger('request')
    logger.info(
        "Request completed",
        method=request.method,
        path=request.path,
        status_code=getattr(g, 'status_code', None),
        duration_ms=round(duration * 1000, 2),
    )

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log an error with context"""
    logger = get_logger('error')
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        exc_info=True,
    )

def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security-related events"""
    logger = get_logger('security')
    logger.warning(
        "Security event",
        event_type=event_type,
        **details,
    )

def log_business_event(event_type: str, details: Dict[str, Any]):
    """Log business events (donations, registrations, etc.)"""
    logger = get_logger('business')
    logger.info(
        "Business event",
        event_type=event_type,
        **details,
    )

def log_performance(operation: str, duration_ms: float, details: Optional[Dict[str, Any]] = None):
    """Log performance metrics"""
    logger = get_logger('performance')
    logger.info(
        "Performance metric",
        operation=operation,
        duration_ms=duration_ms,
        **(details or {}),
    )

# Initialize logging
setup_logging()

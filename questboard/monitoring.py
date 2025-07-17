"""
Monitoring and metrics for QuestBoard.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
import time
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Define metrics
REQUEST_COUNT = Counter(
    'questboard_http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'questboard_http_request_duration_seconds',
    'HTTP Request Latency',
    ['endpoint']
)

DB_QUERY_TIME = Histogram(
    'questboard_db_query_duration_seconds',
    'Database Query Latency',
    ['query_type']
)

ACTIVE_USERS = Gauge('questboard_active_users', 'Number of active users')
QUESTS_CREATED = Counter('questboard_quests_created_total', 'Total quests created')
BOOKMARKS_ADDED = Counter('questboard_bookmarks_added_total', 'Total bookmarks added')

# Database metrics
db_queries = Counter(
    'questboard_db_queries_total',
    'Total database queries',
    ['query_type']
)

def monitor_request(f):
    """Decorator to monitor API requests."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        method = request.method
        endpoint = request.endpoint or 'unknown'
        
        try:
            response = f(*args, **kwargs)
            status_code = response.status_code if hasattr(response, 'status_code') else 200
            
            # Record metrics
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            status_code = 500
            if hasattr(e, 'code') and isinstance(e.code, int):
                status_code = e.code
                
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start_time)
            raise
            
    return wrapper

def monitor_db_query(query_type):
    """Decorator to monitor database queries."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                # Record metrics
                duration = time.time() - start_time
                DB_QUERY_TIME.labels(query_type=query_type).observe(duration)
                db_queries.labels(query_type=query_type).inc()
                
                return result
                
            except Exception as e:
                logger.error(f"Database query failed: {str(e)}", exc_info=True)
                raise
                
        return wrapper
    return decorator

def get_metrics():
    """Return Prometheus metrics."""
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )

def init_monitoring(app):
    """Initialize monitoring for the Flask app."""
    # Add metrics endpoint
    @app.route('/metrics')
    def metrics():
        return get_metrics()
    
    # Register before/after request handlers
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # Skip if the request is for static files
        if request.endpoint == 'static':
            return response
            
        # Calculate request duration
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # Log the request
        logger.info(
            f"{request.method} {request.path} - {response.status_code} "
            f"({duration:.3f}s)"
        )
        
        return response
    
    logger.info("Monitoring initialized")

import functions_framework
from google.cloud import firestore
import json
import time # 🌟 Added for tracking high-resolution execution time
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Initialize Firestore Client
db = firestore.Client()

# This tracks incoming traffic frequency
VISITOR_API_REQUESTS = Counter(
    'portfolio_visitor_requests_total', 
    'Total requests to the visitor counter API', 
    ['method']
)

# 🌟 ADDED: This tracks latency/duration of requests in seconds
# Buckets are in seconds (e.g., .005s, .01s, .025s ... up to 10s)
VISITOR_REQUEST_DURATION = Histogram(
    'portfolio_visitor_request_duration_seconds',
    'Time taken to handle visitor counter API requests',
    ['method']
)

# Pre-register labels on launch so they report 0 instead of nothing
VISITOR_API_REQUESTS.labels(method='GET')
VISITOR_API_REQUESTS.labels(method='POST')
VISITOR_API_REQUESTS.labels(method='OPTIONS')
#FIX: PRE-WARM HISTOGRAM LABELS SO LATENCY PANELS NEVER SHOW NO-DATA
VISITOR_REQUEST_DURATION.labels(method='GET')
VISITOR_REQUEST_DURATION.labels(method='POST')
VISITOR_REQUEST_DURATION.labels(method='OPTIONS')


# This tracks the persistent absolute value from your database
PORTFOLIO_TOTAL_VISITORS = Gauge(
    'portfolio_visitors_total',
    'Actual absolute visitor count synchronized from Firestore'
)

# Initialize metric with live database value on boot
try:
    boot_doc = db.collection('site-data').document('visitors').get()
    if boot_doc.exists:
        initial_count = boot_doc.to_dict().get('count', 0)
        PORTFOLIO_TOTAL_VISITORS.set(initial_count)
    else:
        PORTFOLIO_TOTAL_VISITORS.set(0)
except Exception as boot_err:
    print(f"Warning: Failed to pre-populate metrics metric baseline on startup: {boot_err}")
    PORTFOLIO_TOTAL_VISITORS.set(0)


@functions_framework.http
def increment_visitor_counter(request):
    # Expose the /metrics endpoint for Prometheus scraping
    if request.path.strip('/') == 'metrics':
        try:
            doc_ref = db.collection('site-data').document('visitors').get()
            if doc_ref.exists:
                current_count = doc_ref.to_dict().get('count', 0)
                PORTFOLIO_TOTAL_VISITORS.set(current_count) 
        except Exception as e:
            print(f"Error updating gauge during metrics scrape: {e}")

        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    # 🌟 START THE TIMER
    start_time = time.perf_counter()

    # Track metrics for incoming API traffic (GET, POST, OPTIONS)
    VISITOR_API_REQUESTS.labels(method=request.method).inc()

    # Handle CORS preflight requests from your browser
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Max-Age': '3600'
        }
        # Record duration for OPTIONS request before returning
        VISITOR_REQUEST_DURATION.labels(method=request.method).observe(time.perf_counter() - start_time)
        return ('', 204, headers)

    # Set CORS headers for the main data requests
    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        # Reference the database document create
        doc_ref = db.collection('site-data').document('visitors')

        # === 🚀 METHOD HANDLING SEPARATION ===
        if request.method == 'POST':
            doc_ref.update({'count': firestore.Increment(1)})

        # Fetch the current state of the document (Runs for both GET and POST)
        updated_doc = doc_ref.get()
        current_count = updated_doc.to_dict().get('count', 0)

        # Sync the live database total to your Prometheus telemetry matrix
        PORTFOLIO_TOTAL_VISITORS.set(current_count)

        response_data = {'count': current_count}
        
        # 🌟 RECORD THE METRIC SUCCESS DURATION
        VISITOR_REQUEST_DURATION.labels(method=request.method).observe(time.perf_counter() - start_time)
        return (json.dumps(response_data), 200, headers)

    except Exception as e:
        print(f"Error updating/reading Firestore: {e}")
        # 🌟 RECORD THE METRIC ERROR DURATION ALSO
        VISITOR_REQUEST_DURATION.labels(method=request.method).observe(time.perf_counter() - start_time)
        return (json.dumps({'error': str(e)}), 500, headers)

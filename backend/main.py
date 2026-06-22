import functions_framework
from google.cloud import firestore
import json
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Initialize Firestore Client
db = firestore.Client()

# This tracks incoming traffic frequency
VISITOR_API_REQUESTS = Counter(
    'portfolio_visitor_requests_total', 
    'Total requests to the visitor counter API', 
    ['method']
)

# This tracks the persistent absolute value from your database
PORTFOLIO_TOTAL_VISITORS = Gauge(
    'portfolio_visitors_total',
    'Actual absolute visitor count synchronized from Firestore'
)

# ========================================================
# 🌟 FIX: INITIALIZE METRIC WITH LIVE DATABASE VALUE ON BOOT
# ========================================================
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
        # 🌟 FIX: Force this container to pull the absolute latest value from Firestore
        # right before handing data over to Prometheus.
        try:
            doc_ref = db.collection('site-data').document('visitors').get()
            if doc_ref.exists:
                current_count = doc_ref.to_dict().get('count', 0)
                PORTFOLIO_TOTAL_VISITORS.set(current_count) # Sync memory with live DB
        except Exception as e:
            print(f"Error updating gauge during metrics scrape: {e}")

        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

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
        return ('', 204, headers)

    # Set CORS headers for the main data requests
    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        # Reference the database document create
        doc_ref = db.collection('site-data').document('visitors')

        # === 🚀 METHOD HANDLING SEPARATION ===
        if request.method == 'POST':
            # Atomically increment the count field by 1 ONLY during a POST request
            doc_ref.update({'count': firestore.Increment(1)})

        # Fetch the current state of the document (Runs for both GET and POST)
        updated_doc = doc_ref.get()
        current_count = updated_doc.to_dict().get('count', 0)

        # Sync the live database total to your Prometheus telemetry matrix
        PORTFOLIO_TOTAL_VISITORS.set(current_count)

        response_data = {'count': current_count}
        return (json.dumps(response_data), 200, headers)

    except Exception as e:
        print(f"Error updating/reading Firestore: {e}")
        return (json.dumps({'error': str(e)}), 500, headers)

import functions_framework
from google.cloud import firestore
import json
# 1. Added Gauge import here
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Initialize Firestore Client
db = firestore.Client()

# This tracks incoming traffic frequency
VISITOR_API_REQUESTS = Counter(
    'portfolio_visitor_requests_total', 
    'Total requests to the visitor counter API', 
    ['method']
)

# 2. NEW: This tracks the persistent absolute value from your database
PORTFOLIO_TOTAL_VISITORS = Gauge(
    'portfolio_visitors_total',
    'Actual absolute visitor count synchronized from Firestore'
)


@functions_framework.http
def increment_visitor_counter(request):
    # 3. Expose the /metrics endpoint for Prometheus scraping
    if request.path.strip('/') == 'metrics':
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

        # 3. NEW: Sync the live database total to your Prometheus telemetry matrix
        PORTFOLIO_TOTAL_VISITORS.set(current_count)

        response_data = {'count': current_count}
        return (json.dumps(response_data), 200, headers)

    except Exception as e:
        print(f"Error updating/reading Firestore: {e}")
        return (json.dumps({'error': str(e)}), 500, headers)

import functions_framework
from google.cloud import firestore
import json
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# Initialize Firestore Client
db = firestore.Client()

VISITOR_API_REQUESTS = Counter(
    'portfolio_visitor_requests_total', 
    'Total requests to the visitor counter API', 
    ['method']
)


@functions_framework.http
def increment_visitor_counter(request):
    # 3. Expose the /metrics endpoint for Prometheus scraping
    # We strip trailing slashes to catch both "/metrics" and "/metrics/"
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

        response_data = {'count': current_count}
        return (json.dumps(response_data), 200, headers)

    except Exception as e:
        print(f"Error updating/reading Firestore: {e}")
        return (json.dumps({'error': str(e)}), 500, headers)

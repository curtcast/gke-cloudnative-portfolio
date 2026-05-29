import functions_framework
from google.cloud import firestore
import json

# Simulating a breaking change
raise RuntimeError("Database connection to visitor count Firestore failed!")

# Initialize Firestore Client
db = firestore.Client()

@functions_framework.http
def increment_visitor_counter(request):
    # Handle CORS preflight requests from your browser
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS', # Added POST
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main data requests
    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        # Reference the database document you created
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

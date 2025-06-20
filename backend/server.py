# server.py for Python Flask Secure Build (Secure Error Handling)

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sys
import traceback
import logging

app = Flask(__name__)

# Configure logging for internal server errors
# This ensures stack traces are logged to a file or stdout/stderr
# but NOT sent to the client.
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app_errors.log', # Log to a file
                    filemode='a') # Append to the log file
# Also log to stderr for immediate console visibility during development
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


# In a real application, you would specify allowed origins for security.
# For a secure build, explicitly list allowed origins, rather than '*'
# For this demo, we'll keep '*' for ease of testing with React app on different port
CORS(app) 

# --- SECURE ENDPOINT ---
@app.route('/api/error/trigger', methods=['POST'])
def trigger_error():
    print('--- RECEIVED REQUEST TO TRIGGER ERROR ---')
    data = request.get_json(silent=True)
    simulated_input = data.get('simulatedInput', 'null') if data else 'null'
    print(f'Input received from client: "{simulated_input}"')
    print('--- DEMO: Triggering Handled Exception for Secure Error Handling ---')
    
    try:
        # Simulate an operation that could cause an error
        # For demonstration, still causing a ZeroDivisionError, but it's handled.
        result = 1 / 0 
        
        return jsonify({"message": "This should not be reached if an error occurs."}), 200

    except Exception as e:
        # --- SECURE ERROR HANDLING ---
        # 1. Log the full traceback internally
        app.logger.error(f"An error occurred during processing: {e}", exc_info=True)
        print("--- SECURE: FULL STACK TRACE LOGGED INTERNALLY, NOT EXPOSED TO CLIENT ---")
        
        # 2. Return a generic, non-informative error message to the client
        return jsonify({"message": "An internal server error occurred. Please try again later."}), 500


# --- SECURE: Generic Error Handler for any unhandled 500s ---
# This catches any 500 errors that are *not* caught by specific try-except blocks
# It ensures no stack traces are exposed even for unexpected errors.
@app.errorhandler(500)
def handle_secure_500(e):
    # Log the full exception information internally
    app.logger.error(f"An unhandled internal server error occurred: {e}", exc_info=True)
    print("--- SECURE: UNHANDLED 500 ERROR CAUGHT. STACK TRACE LOGGED INTERNALLY, NOT EXPOSED TO CLIENT ---", file=sys.stderr)
    
    # Return a generic error message to the client.
    # The client receives a simple JSON response, not an HTML page with traces.
    response = jsonify({"message": "An unexpected internal server error occurred. Please contact support if the issue persists."})
    response.status_code = 500
    
    # Ensure CORS headers are present for the secure error response as well
    # Even in secure builds, cross-origin requests need these headers
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")

    return response


# Start the server and listen on the specified port
if __name__ == '__main__':
    print("Python Flask Secure Backend (Error Handling) listening on http://127.0.0.1:5002")
    print("Ready to demonstrate secure error handling.")
    app.run(debug=False, port=5002) # debug=False for production readiness
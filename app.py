from flask import Flask, request, jsonify
from flask.logging import create_logger
import logging
import os # Import the os module

import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
LOG = create_logger(app)
LOG.setLevel(logging.INFO)

def scale(payload):
    """Scales Payload"""

    LOG.info("Scaling Payload: %s payload")
    scaler = StandardScaler().fit(payload)
    scaled_adhoc_predict = scaler.transform(payload)
    return scaled_adhoc_predict

@app.route("/")
def home():
    html = "<h3>Sklearn Prediction Home CI/CD Pipeline with AzureDevops 2</h3>"
    return html.format(format)

@app.route("/predict", methods=['POST'])
def predict():
    """Performs an sklearn prediction

    input looks like:
            {
    "CHAS":{
      "0":0
    },
    "RM":{
      "0":6.575
    },
    "TAX":{
      "0":296.0
    },
    "PTRATIO":{
       "0":15.3
    },
    "B":{
       "0":396.9
    },
    "LSTAT":{
       "0":4.98
    }

    result looks like:
    { "prediction": [ 20.35373177134412 ] }

    """
    json_payload = request.json
    
    # Specify the expected exception type: FileNotFoundError
    try:
        clf = joblib.load("Housing_price_model/LinearRegression.joblib")
    except FileNotFoundError: # Changed from bare except
        LOG.info("Model file not found: boston_housing_prediction.joblib")
        return "Model not loaded", 404 # Return a 404 status code for clarity

    LOG.info("JSON payload: %s", json_payload)
    
    inference_payload = pd.DataFrame(json_payload)
    LOG.info("inference payload DataFrame: %s", inference_payload)
    
    scaled_payload = scale(inference_payload)
    prediction = list(clf.predict(scaled_payload))
    LOG.info("Prediction value: %s", prediction)
    
    return jsonify({'Prediction': prediction})

if __name__ == "__main__":
    # Load the model outside the request handler to avoid repeated loading
    # and verify its presence at startup
    model_path = "Housing_price_model/LinearRegression.joblib"
    if not os.path.exists(model_path):
        LOG.error(f"Error: Model file '{model_path}' not found!")
        # You might want to exit or handle this more robustly in production
    
    app.run(host='0.0.0.0', port=8000, debug=True)
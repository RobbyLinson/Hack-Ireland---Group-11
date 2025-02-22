import json
from fastapi.testclient import TestClient
from nlp_model import app  # ✅ Now imports from nlp_model.py
import pytest
import os

# Initialize test client
client = TestClient(app)

# Define file paths
TEST_FILE = "test_input.json"
OUTPUT_FILE = "output.json"

def test_analyze_bias():
    # Ensure the input file exists
    if not os.path.exists(TEST_FILE):
        raise FileNotFoundError(f"Error: The file '{TEST_FILE}' was not found. Make sure it exists.")

    # Load test data from JSON file
    with open(TEST_FILE, "r") as file:
        test_data = json.load(file)

    # Send request to FastAPI endpoint
    response = client.post("/analyze/", json=test_data)
    
    # Ensure request was successful
    assert response.status_code == 200  
    json_data = response.json()

    # Extract raw bias scores
    bias_scores = json_data.get("bias_analysis", {})
    left = bias_scores.get("Left", 0)
    center = bias_scores.get("Center", 0)
    right = bias_scores.get("Right", 0)

    # Determine if the text is biased
    bias_threshold = 0.5  # Adjust as needed
    is_biased = left > bias_threshold or right > bias_threshold

    # Print the results
    print("\nAPI Response:", json_data)
    print(f"Left: {left:.4f}, Center: {center:.4f}, Right: {right:.4f}")
    print(f"Bias Detected: {'YES' if is_biased else 'NO'}")

    # Save only raw bias scores to output.json
    output_data = {
        "Left": left,
        "Center": center,
        "Right": right
    }

    with open(OUTPUT_FILE, "w") as outfile:
        json.dump(output_data, outfile, indent=4)

    print(f"Raw bias scores saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    test_analyze_bias()

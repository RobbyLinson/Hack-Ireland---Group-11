from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Initialize FastAPI app
app = FastAPI()

# Load PoliticalBiasBERT model
MODEL_NAME = "bucketresearch/politicalBiasBERT"
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Define input structure
class TextRequest(BaseModel):
    text: str

# Define endpoint
@app.post("/analyze/")
async def analyze_bias(request: TextRequest):
    try:
        inputs = tokenizer(request.text, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
            probabilities = logits.softmax(dim=-1)[0].tolist()

        categories = ["Left", "Middle", "Right"]
        bias_result = {categories[i]: probabilities[i] for i in range(len(categories))}

        return {"bias_analysis": bias_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run using: uvicorn nlp_model:app --reload
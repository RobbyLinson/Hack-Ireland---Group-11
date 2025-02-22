from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to analyze text bias
def GPT_ana(text, bias_level):
    """
    Analyze the text and determine why it is biased.

    Parameters:
    text (str): The chunk of text to analyze.
    bias_level (dict): A dictionary with keys 'Left', 'Middle', 'Right' and values between 0 and 1.

    Returns:
    str: Explanation of why the text is biased.
    """
    # Validate bias_level keys
    required_keys = ['Left', 'Middle', 'Right']
    for key in required_keys:
        if key not in bias_level:
            raise ValueError(f"Missing key '{key}' in bias_level dictionary")

    # Prepare the prompt for ChatGPT
    prompt = f"Analyze the following text and explain why it is biased:\n\n{text}\n\nBias levels:\nLeft: {bias_level['Left']}\nMiddle: {bias_level['Middle']}\nRight: {bias_level['Right']}\n\nExplanation:"

    # Call the OpenAI API
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=150)

    # Extract the explanation from the response
    explanation = response.choices[0].message.content.strip()
    return explanation
import requests
import os
from dotenv import load_dotenv

# ✅ Load the Gemini API key from the .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("REACT_APP_GEMINI_API_KEY")

# ✅ Gemini endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# ✅ Headers for the request
headers = {
    "Content-Type": "application/json"
}

def get_sentiment(feedback_text):
    """
    Uses Gemini AI to classify the sentiment of a feedback string as:
    Positive, Negative, or Neutral.
    """
    prompt = f"""
    You are a sentiment analysis expert. Analyze the following customer feedback and respond ONLY 
    with one word: Positive, Negative, or Neutral.
    
    Feedback: "{feedback_text}"
    """

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        # ✅ Extract and return sentiment text
        if "candidates" in response_data:
            sentiment = response_data["candidates"][0]["content"]["parts"][0]["text"]
            return sentiment.strip()
        else:
            return "Unknown"

    except Exception as e:
        print(f"❌ Sentiment Analysis Error: {e}")
        return "Unknown"


# ✅ Test the function
if __name__ == "__main__":
    feedback = "The staff is well organized"
    sentiment_result = get_sentiment(feedback)
    print("🧠 Sentiment:", sentiment_result)

import requests
import os
from dotenv import load_dotenv

# ✅ Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("REACT_APP_GEMINI_API_KEY")

def get_ai_suggestion(feedback_text, category, product):
    """
    Sends customer feedback along with category and product info to Google Gemini AI
    and returns actionable suggestions for shop owners.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    prompt = f"""
You are an expert business consultant helping a retail shop owner improve a specific product based on customer feedback.

🎯 Customer Feedback: "{feedback_text}"
📦 Product: {product}
🏷️ Category: {category}

✅ Task: Give 2–3 direct and **practical suggestions** for improving the **{product}** based on the above feedback.

🔒 Rules:
- DO NOT say the feedback is vague or unclear.
- DO NOT make generic suggestions.
- Each suggestion must be relevant to the product and feedback.
- Format: 
1. Suggestion: <text>
   Why it helps: <brief reason>
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

        if "candidates" in response_data:
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "AI could not generate a valid suggestion."

    except Exception as e:
        print(f"❌ AI Suggestion Error: {e}")
        return "AI could not generate suggestions."

# ✅ Test this module independently
if __name__ == "__main__":
    feedback = "No Use sulfate-free and natural ingredients"
    category = "Haircare"
    product = "Shampoo"
    suggestion = get_ai_suggestion(feedback, category, product)
    print("📢 AI Suggestion:\n", suggestion)
